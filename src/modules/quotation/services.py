"""
Services layer for the Premium Quotation module.
Defines computation logic and mock ML regressors (XGBoost/LightGBM).
"""

import logging
from typing import Dict, Any
from src.modules.quotation.validators import QuotationInputValidator

logger = logging.getLogger(__name__)


import logging
import time
from datetime import datetime
from typing import Dict, Any
from src.modules.quotation.validators import QuotationInputValidator
from src.ml.preprocessing.data_loader import DataLoader
from src.ml.inference.quotation_predictor import QuotationPredictor
from src.database.session import SessionLocal
from src.repositories.user import UserRepository
from src.repositories.quotation import QuotationRepository
from src.repositories.prediction import PredictionRepository
from src.services.user_service import UserService
from src.services.quotation_service import QuotationService as DBQuotationService
from src.services.prediction_service import PredictionService
from src.ml.inference.prediction_logger import PredictionLogger

logger = logging.getLogger(__name__)


class QuotationService:
    """
    Handles core underwriting and premium prediction business tasks.
    """

    def generate_premium_quote(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validates user properties and calculates vehicle insurance policy quotations.
        Uses Pydantic validator, loads baseline template CSV, executes prediction, and saves history.

        Args:
            input_data: Uncompiled dictionary containing quotation inputs.

        Returns:
            Dictionary containing premium quotes, explainability matrices, and status details.
        """
        start_time = time.perf_counter()

        # Validate parameters structural correctness
        validated = QuotationInputValidator(**input_data)
        logger.info(f"Generating quotation quote for customer: {validated.customer_name}")

        # Construct raw inputs using CSV template row for robustness
        is_car = (validated.vehicle_type == "Car")
        dataset_filename = "acko_car_quotation.csv" if is_car else "acko_bike_quotation.csv"
        df_tpl = DataLoader.load_csv(dataset_filename).head(1)
        row_dict = df_tpl.to_dict(orient="records")[0]

        # Overwrite fields from user form validation
        row_dict["customer_age"] = int(validated.age)
        row_dict["city"] = str(validated.city)
        row_dict["state"] = str(validated.state)
        row_dict["vehicle_make"] = str(validated.manufacturer)
        row_dict["vehicle_model"] = str(validated.model)
        row_dict["fuel_type"] = str(validated.fuel_type)
        row_dict["idv"] = float(validated.vehicle_idv)
        row_dict["ncb_percent"] = float(validated.ncb_percentage)
        row_dict["claim_history_count"] = 1 if validated.previous_claims else 0
        row_dict["vehicle_age_years"] = max(0, datetime.now().year - int(validated.manufacturing_year))

        # Filter targets and leakages
        leakages = ["od_premium_before_ncb", "ncb_discount_amount", "tp_premium", "addon_premium", "gst_amount", "annual_premium"]
        clean_row = {k: v for k, v in row_dict.items() if k not in leakages}

        # Predict
        predictor = QuotationPredictor(vehicle_type="car" if is_car else "bike")
        pred_res = predictor.predict(clean_row)

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        # Persist to PostgreSQL database using Transaction isolation block
        import src.database.database as db_module
        if db_module.engine is not None:
            SessionLocal.configure(bind=db_module.engine)
        session = SessionLocal()
        try:
            # Service components
            user_repo = UserRepository(session)
            quote_repo = QuotationRepository(session)
            pred_repo = PredictionRepository(session)

            user_service = UserService(user_repo)
            db_quote_service = DBQuotationService(quote_repo, user_repo)
            pred_service = PredictionService(pred_repo)

            # Ensure default customer exists
            try:
                user = user_service.get_user_by_email("customer@acko.com")
            except Exception:
                user = user_service.register_user(
                    full_name=validated.customer_name,
                    email="customer@acko.com",
                    phone_number=validated.mobile_number,
                    role="customer"
                )

            # Clean any float NaN values from the inputs dictionary to ensure valid JSON representation in PostgreSQL
            import math
            import pandas as pd
            db_clean_row = {
                k: (None if (isinstance(v, float) and (math.isnan(v) or pd.isna(v))) else v)
                for k, v in clean_row.items()
            }

            # Save quotation
            db_quote_service.create_quotation(
                user_id=user.id,
                quotation_type=pred_res["prediction_type"],
                vehicle_type="car" if is_car else "bike",
                input_json=db_clean_row,
                predicted_premium=pred_res["predicted_premium"],
                model_version=pred_res["model_version"]
            )

            # Save Prediction Telemetry Log
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
        except Exception as db_err:
            session.rollback()
            logger.error(f"Error persisting quotation data: {db_err}", exc_info=True)
            # Re-raise to let Page handler notify Streamlit cleanly
            raise db_err
        finally:
            session.close()

        return {
            "status": "success",
            "predicted_premium": pred_res["predicted_premium"],
            "confidence_score": pred_res["confidence_metadata"]["confidence_score"],
            "model_version": pred_res["model_version"],
            "timestamp": pred_res["timestamp"],
            "top_positive_features": pred_res["top_positive_features"],
            "top_negative_features": pred_res["top_negative_features"],
            "shap_summary": pred_res["shap_summary"],
        }
