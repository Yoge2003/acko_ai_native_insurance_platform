"""
Service layer for the Claims module.
Defines mock claims filing procedures.
"""

import logging
from datetime import datetime
from typing import Dict, Any
from src.modules.claims.validators import ClaimInputValidator
from src.utils.common import generate_uuid

logger = logging.getLogger(__name__)


import logging
import time
from datetime import datetime, timedelta
from typing import Dict, Any
from src.modules.claims.validators import ClaimInputValidator
from src.utils.common import generate_uuid
from src.ml.preprocessing.data_loader import DataLoader
from src.ml.inference.claims_predictor import ClaimsPredictor
from src.database.session import SessionLocal
from src.repositories.user import UserRepository
from src.repositories.policy import PolicyRepository
from src.repositories.claim import ClaimRepository
from src.repositories.prediction import PredictionRepository
from src.repositories.image import UploadedImageRepository
from src.services.user_service import UserService
from src.services.policy_service import PolicyService
from src.services.claim_service import ClaimService as DBClaimService
from src.services.prediction_service import PredictionService
from src.services.image_service import ImageService
from src.ml.inference.prediction_logger import PredictionLogger

logger = logging.getLogger(__name__)

import io
import json
from PIL import Image, ImageOps
import google.generativeai as genai
from src.config.settings import settings

VISION_PROMPT = """
You are an expert vehicle insurance claims adjuster. Analyze this photo of vehicle damage and return a structured JSON object.
Provide your evaluation in the following JSON format:
{
  "damaged_parts": ["bumper", "hood", "headlight"],
  "damage_severity": "Low" or "Medium" or "High",
  "estimated_repair_complexity": "Low" or "Medium" or "High",
  "visible_fraud_indicators": ["none" or list of suspect signs],
  "confidence_score": 0.95,
  "natural_language_assessment": "Comprehensive summary of visible damage reasons",
  "damage_type": "Body" or "Windshield" or "Engine" or "Bumper"
}

Ground rules:
1. "damaged_parts" must only include parts visible in the image. Common parts: bumper, windshield, headlight, hood, door_panel, side_mirror, etc.
2. "confidence_score" must be a float between 0.0 and 1.0 representing your analysis certainty.
3. Be objective. If no fraud indicators are visible, set "visible_fraud_indicators" to ["none"].
4. Choose "damage_type" from ["Body", "Windshield", "Engine", "Bumper"] matching the primary damaged component.
"""

def validate_and_preprocess_image(uploaded_file) -> Image.Image:
    """
    Validates and preprocesses target uploaded collision files:
    - size limit check (< 10MB)
    - verification that file opens as image
    - EXIF orientation transpose correction
    - mode normalization (to RGB)
    - resolution check (min 200x200)
    - resize restriction (max 1024x1024)
    """
    uploaded_file.seek(0, io.SEEK_END)
    file_size = uploaded_file.tell()
    uploaded_file.seek(0)
    
    if file_size > 10 * 1024 * 1024:
        raise ValueError("Image file size exceeds the maximum limit of 10MB.")
        
    try:
        img = Image.open(uploaded_file)
        img.verify()
        uploaded_file.seek(0)
        img = Image.open(uploaded_file)
    except Exception as e:
        raise ValueError(f"Invalid image format or corrupted file: {e}")
        
    # EXIF orientation transpose
    img = ImageOps.exif_transpose(img)
    
    # Normalizer
    if img.mode != 'RGB':
        img = img.convert('RGB')
        
    # Quality resolution check
    width, height = img.size
    if width < 200 or height < 200:
        raise ValueError(f"Image resolution too low ({width}x{height}). Minimum required is 200x200.")
        
    # Resize
    max_dim = 1024
    if width > max_dim or height > max_dim:
        ratio = min(max_dim / width, max_dim / height)
        new_size = (int(width * ratio), int(height * ratio))
        img = img.resize(new_size, Image.Resampling.LANCZOS)
        
    return img

def analyze_damage_image(img: Image.Image, api_key: str) -> Dict[str, Any]:
    """
    Integrates Gemini Vision model to extract structured damage metrics.
    Retries up to 3 times on quota/transient errors before raising to trigger fallback.
    """
    import google.api_core.exceptions
    from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type, before_sleep_log

    if not api_key or api_key == "your_gemini_api_key_here":
        raise ValueError("Gemini API key is unconfigured.")

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.0-flash")

        @retry(
            reraise=True,
            stop=stop_after_attempt(3),
            wait=wait_exponential(multiplier=1, min=1, max=4),
            retry=retry_if_exception_type((
                google.api_core.exceptions.ResourceExhausted,
                google.api_core.exceptions.ServiceUnavailable,
                google.api_core.exceptions.DeadlineExceeded
            )),
            before_sleep=before_sleep_log(logger, logging.WARNING)
        )
        def _call_vision():
            logger.info("Issuing Gemini Vision generate_content call for damage analysis...")
            return model.generate_content(
                [img, VISION_PROMPT],
                generation_config={"response_mime_type": "application/json"}
            )

        response = _call_vision()
        data = json.loads(response.text)
        required_keys = {
            "damaged_parts",
            "damage_severity",
            "estimated_repair_complexity",
            "visible_fraud_indicators",
            "confidence_score",
            "natural_language_assessment",
            "damage_type"
        }
        for k in required_keys:
            if k not in data:
                raise ValueError(f"Missing key in response: {k}")
        return data
    except Exception as e:
        logger.error(f"Gemini Vision call failed: {e}. Executing pipeline fallback.", exc_info=True)
        raise e


class ClaimsService:
    """
    Business service layer orchestrating vehicle collision claim workflows.
    """

    def submit_claim_request(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validates claim inputs, evaluates approval prediction using ClaimsPredictor,
        and persists claim details and image logs into PostgreSQL.

        Args:
            payload: Dict of forms values.

        Returns:
            Dictionary containing claim outcomes, shap feature weights, and database references.
        """
        start_time = time.perf_counter()

        # Ensure a Claim ID is generated for tracking if missing
        if not payload.get("claim_id"):
            payload["claim_id"] = f"CLM-{generate_uuid()[:8].upper()}"

        # Validate structure using Pydantic schema
        validated = ClaimInputValidator(**payload)
        logger.info(f"Filing new claim request {validated.claim_id} for policy {validated.policy_number}")
        
        # Load CSV template row for claims pred features
        is_car = (validated.vehicle_type == "Car")
        dataset_filename = "acko_car_claims.csv" if is_car else "acko_bike_claims.csv"
        df_tpl = DataLoader.load_csv(dataset_filename).head(1)
        row_dict = df_tpl.to_dict(orient="records")[0]

        # Overwrite defaults
        row_dict["claim_amount"] = float(validated.claim_amount)
        row_dict["incident_date"] = datetime.now().strftime("%Y-%m-%d")
        row_dict["incident_month"] = datetime.now().month
        
        # Check if an image is uploaded and perform visual RAG pipeline
        uploaded_file = payload.get("uploaded_image")
        gemini_analysis = None
        processed_img = None
        
        if uploaded_file is not None:
            try:
                # 1. Image validation & preprocessing
                processed_img = validate_and_preprocess_image(uploaded_file)
                # 2. Gemini Vision integration
                gemini_analysis = analyze_damage_image(processed_img, settings.GEMINI_API_KEY)
            except Exception as e:
                logger.error(f"Collision photo analysis failed: {e}. Applying fallback heuristics.")
                # Fallback implementation
                parts = []
                desc_lower = validated.description.lower()
                for p in ["bumper", "windshield", "headlight", "hood", "mirror", "door"]:
                    if p in desc_lower:
                        parts.append(p)
                if not parts:
                    parts = ["bumper"]
                
                severity = "Medium"
                if "severe" in desc_lower or "major" in desc_lower or "shattered" in desc_lower or validated.claim_amount > 100000:
                    severity = "High"
                elif "scratch" in desc_lower or "minor" in desc_lower or validated.claim_amount < 20000:
                    severity = "Low"
                    
                damage_type = "Body"
                if "windshield" in desc_lower or "mirror" in desc_lower or "glass" in desc_lower:
                    damage_type = "Windshield"
                elif "engine" in desc_lower or "radiator" in desc_lower:
                    damage_type = "Engine"
                elif "bumper" in desc_lower:
                    damage_type = "Bumper"

                gemini_analysis = {
                    "damaged_parts": parts,
                    "damage_severity": severity,
                    "estimated_repair_complexity": severity,
                    "visible_fraud_indicators": ["none"],
                    "confidence_score": 0.5,
                    "damage_type": damage_type,
                    "natural_language_assessment": f"⚠️ [Vision Fallback Mode] Photo assessment unavailable. Heuristics details: {validated.description[:150]}"
                }
        else:
            # Fallback when no image is uploaded
            parts = []
            desc_lower = validated.description.lower()
            for p in ["bumper", "windshield", "headlight", "hood", "mirror", "door"]:
                if p in desc_lower:
                    parts.append(p)
            if not parts:
                parts = ["bumper"]
            
            severity = "Medium"
            if "severe" in desc_lower or "major" in desc_lower or "shattered" in desc_lower or validated.claim_amount > 100000:
                severity = "High"
            elif "scratch" in desc_lower or "minor" in desc_lower or validated.claim_amount < 20000:
                severity = "Low"
                
            damage_type = "Body"
            if "windshield" in desc_lower or "mirror" in desc_lower or "glass" in desc_lower:
                damage_type = "Windshield"
            elif "engine" in desc_lower or "radiator" in desc_lower:
                damage_type = "Engine"
            elif "bumper" in desc_lower:
                damage_type = "Bumper"

            gemini_analysis = {
                "damaged_parts": parts,
                "damage_severity": severity,
                "estimated_repair_complexity": severity,
                "visible_fraud_indicators": ["none"],
                "confidence_score": 0.5,
                "damage_type": damage_type,
                "natural_language_assessment": f"⚠️ [Vision Fallback Mode] No claims image submitted. Heuristics details: {validated.description[:150]}"
            }

        # Overtake claims feature engineering inputs with Gemini Vision results
        severity_score_map = {"Low": 2.5, "Medium": 5.0, "High": 8.5}
        severity_score = severity_score_map.get(gemini_analysis.get("damage_severity", "Medium"), 5.0)
        
        row_dict["damage_severity_score"] = severity_score
        row_dict["num_parts_affected"] = len(gemini_analysis.get("damaged_parts", ["bumper"]))
        row_dict["affected_parts"] = ", ".join(gemini_analysis.get("damaged_parts", ["bumper"]))
        row_dict["damage_type"] = gemini_analysis.get("damage_type", "Body")

        # Exclude targets
        leakages = ["approval_probability", "claim_approved"]
        clean_row = {k: v for k, v in row_dict.items() if k not in leakages}

        # Predict
        predictor = ClaimsPredictor(vehicle_type="car" if is_car else "bike")
        pred_res = predictor.predict(clean_row)

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        # Persist into DB
        import src.database.database as db_module
        if db_module.engine is not None:
            SessionLocal.configure(bind=db_module.engine)
        session = SessionLocal()
        try:
            user_repo = UserRepository(session)
            policy_repo = PolicyRepository(session)
            claim_repo = ClaimRepository(session)
            pred_repo = PredictionRepository(session)
            image_repo = UploadedImageRepository(session)

            user_service = UserService(user_repo)
            policy_service = PolicyService(policy_repo, user_repo)
            db_claim_service = DBClaimService(claim_repo, policy_repo, user_repo)
            pred_service = PredictionService(pred_repo)
            db_image_service = ImageService(image_repo, claim_repo)

            # Ensure default customer exists
            try:
                user = user_service.get_user_by_email("customer@acko.com")
            except Exception:
                user = user_service.register_user(
                    full_name="Jane Doe",
                    email="customer@acko.com",
                    phone_number="+919876543210",
                    role="customer"
                )

            # Find or dynamically register policy details
            policy = policy_repo.get_by_policy_number(validated.policy_number)
            if policy is None:
                policy = policy_service.create_policy(
                    user_id=user.id,
                    policy_number=validated.policy_number,
                    vehicle_type="car" if is_car else "bike",
                    vehicle_make="Honda" if is_car else "Hero",
                    vehicle_model="City" if is_car else "Splendor",
                    registration_number="MH-02-AB-1234",
                    idv=max(2000000.0, validated.claim_amount * 1.5),
                    premium=30000.0,
                    policy_type="Comprehensive",
                    coverage_type="Own Damage",
                    policy_start_date=datetime.utcnow() - timedelta(days=30),
                    policy_end_date=datetime.utcnow() + timedelta(days=335)
                )

            # Submit claim
            decision = "approved" if pred_res["claim_prediction"] else "rejected"
            claim = db_claim_service.submit_claim(
                policy_id=policy.id,
                user_id=user.id,
                claim_amount=validated.claim_amount,
                damage_summary=validated.description,
                gemini_analysis_json=gemini_analysis,
                predicted_decision=decision,
                approval_probability=pred_res["approval_probability"]
            )

            # Save uploaded image file metadata if exists
            if uploaded_file is not None and processed_img is not None:
                import os
                os.makedirs("reports/attachments", exist_ok=True)
                local_path = os.path.abspath(os.path.join("reports/attachments", uploaded_file.name))
                
                # Save preprocessed normalized JPEG
                processed_img.save(local_path, format="JPEG", quality=90)

                db_image_service.register_image(
                    claim_id=claim.id,
                    original_filename=uploaded_file.name,
                    local_path=local_path
                )

            # Clean any float NaN values from the inputs dictionary to ensure consistency
            import math
            import pandas as pd
            db_clean_row = {
                k: (None if (isinstance(v, float) and (math.isnan(v) or pd.isna(v))) else v)
                for k, v in clean_row.items()
            }

            # Save Telemetry Logs page
            input_hash = PredictionLogger.compute_input_hash(pd.DataFrame([db_clean_row]))
            pred_hash = PredictionLogger.compute_prediction_hash(pred_res)
            
            pred_service.log_prediction(
                prediction_type=pred_res["prediction_type"],
                model_version=pred_res["model_version"],
                latency_ms=int(latency_ms),
                input_hash=input_hash,
                output_hash=pred_hash
            )

            session.commit()
        except Exception as err:
            session.rollback()
            logger.error(f"Error persisting claim details: {err}", exc_info=True)
            raise err
        finally:
            session.close()

        # Configured threshold for human review (e.g. 0.70 confidence)
        human_review = float(pred_res["confidence"]) < 0.70

        return {
            "status": "Submitted",
            "claim_id": validated.claim_id,
            "policy_number": validated.policy_number,
            "route": "Manual Investigation Queue" if human_review else "Auto-Fast-Track Queue",
            "submitted_at": pred_res["timestamp"],
            "model_version": pred_res["model_version"],
            "approval_decision": decision.upper(),
            "approval_probability": pred_res["approval_probability"],
            "confidence": pred_res["confidence"],
            "top_positive_features": pred_res["top_positive_features"],
            "top_negative_features": pred_res["top_negative_features"],
            "shap_summary": pred_res["shap_summary"],
            "human_review_flag": human_review,
            "gemini_analysis": gemini_analysis,
            "detail_summary": f"Claim request of ₹{validated.claim_amount:,} registered for review."
        }
