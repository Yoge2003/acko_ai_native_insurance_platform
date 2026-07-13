"""
Prediction Pipeline.
Official inference pipeline executing validation -> preprocessing -> features -> encoding -> predictions -> SHAP.
"""

import time
import logging
from datetime import datetime
from typing import Dict, Any, List, Union
import pandas as pd
import numpy as np

from src.ml.inference.model_loader import ModelLoader
from src.ml.inference.pipeline_validator import PipelineValidator, PipelineValidationError
from src.ml.inference.prediction_logger import PredictionLogger
from src.ml.feature_engineering.feature_pipeline import run_feature_pipeline, PIPELINE_MAP
from src.ml.training.training_pipeline import TrainingPipeline

# Set up logger
logger = logging.getLogger(__name__)


class PredictionPipeline:
    """
    Main orchestrator for real-time model inference.
    """

    @classmethod
    def run_inference(
        cls,
        dataset_type: str,
        raw_input: Union[Dict[str, Any], List[Dict[str, Any]], pd.DataFrame]
    ) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """
        Executes end-to-end inference flow on incoming user records.
        Handles both single data objects and bulk cohorts in batches.

        Args:
            dataset_type: Target category string ('car_quotation', etc.).
            raw_input: Unprocessed dataset structure.

        Returns:
            Union[Dict[str, Any], List[Dict[str, Any]]]: Structured estimation object(s).
        """
        start_time = time.perf_counter()
        
        # 1. Format raw input to standard DataFrame
        is_single_prediction = False
        if isinstance(raw_input, pd.DataFrame):
            df_raw = raw_input.copy()
        elif isinstance(raw_input, list):
            df_raw = pd.DataFrame(raw_input)
        elif isinstance(raw_input, dict):
            df_raw = pd.DataFrame([raw_input])
            is_single_prediction = True
        else:
            raise PipelineValidationError(
                f"Unsupported raw input data format: {type(raw_input)}. "
                "Must be a dictionary, list of dictionaries, or pandas DataFrame."
            )

        # Standardize column headers of raw input (spaces/dashes to underscores, lowercase)
        df_raw.columns = (
            df_raw.columns.str.strip()
            .str.lower()
            .str.replace(" ", "_")
            .str.replace("-", "_")
        )

        # 2. Retrieve preprocessing specs
        if dataset_type not in PIPELINE_MAP:
            raise PipelineValidationError(f"Unknown dataset type: {dataset_type}")

        preprocessor_class = PIPELINE_MAP[dataset_type]["preprocessor"]
        required_cols = preprocessor_class.REQUIRED_COLS
        leakage_cols = preprocessor_class.LEAKAGE_COLS
        identity_cols = getattr(preprocessor_class, "IDENTIFIER_COLS", [])
        
        # Extract target name
        target_col = "claim_approved" if "claims" in dataset_type else "annual_premium"

        # Determine features that the caller MUST supply (ignore leakage, target, and identifiers)
        target_leakage_and_identifiers = leakage_cols + identity_cols + [target_col]
        inference_features = [col for col in required_cols if col not in target_leakage_and_identifiers]

        # 3. Load model components (cached)
        model, transformer, artifacts = ModelLoader.load_components(dataset_type)
        metadata = artifacts.get("metadata", {})
        feature_names = artifacts.get("feature_names", [])

        # 4. Perform Raw Input Validation
        # Clean dataframe copy focusing validation on user features (exclude targets, leakages, and identifiers)
        df_validation = df_raw.drop(columns=[col for col in target_leakage_and_identifiers if col in df_raw.columns], errors="ignore")
        
        PipelineValidator.validate_raw_input(
            df_raw=df_validation,
            expected_raw_features=inference_features,
            artifact_metadata={"model_version": metadata.get("model_version", "1.0.0")}
        )

        # 5. Inject place-holder values for identifiers and leakages to satisfy preprocessor constraints
        df_raw_filled = df_raw.copy()
        for col in required_cols:
            if col not in df_raw_filled.columns:
                if col in ["record_id"]:
                    df_raw_filled[col] = "inf_rec"
                elif col in ["manufacturing_year"]:
                    df_raw_filled[col] = 2026
                elif col in ["colour"]:
                    df_raw_filled[col] = "blue"
                elif col in ["incident_date"]:
                    df_raw_filled[col] = "2026-07-09"
                elif col in ["zero_dep_addon", "engine_protection_addon", "previous_claims_count", "ncb_at_claim_percent", "num_parts_affected", "claim_approved"]:
                    df_raw_filled[col] = 0
                elif col in ["annual_premium", "approval_probability"]:
                    df_raw_filled[col] = 0.0
                elif col in leakage_cols:
                    df_raw_filled[col] = 0.0
                else:
                    df_raw_filled[col] = 0

        # Adjust correct column order expected by preprocessor
        df_raw_filled = df_raw_filled[required_cols]

        # 6. Preprocessing & Feature Engineering
        df_engineered = run_feature_pipeline(df_raw_filled, dataset_type)

        # Ensure target is absent
        if target_col in df_engineered.columns:
            df_engineered = df_engineered.drop(columns=[target_col])

        # 7. Apply ColumnTransformer Encoders
        X_encoded_raw = transformer.transform(df_engineered)
        
        # Sanitize column headers (LightGBM/XGBoost formatting)
        X_encoded = TrainingPipeline.sanitize_column_names(X_encoded_raw)

        # Align column ordering strictly matching training names
        X_encoded = X_encoded[feature_names]

        # 8. Post-Transformation validation
        PipelineValidator.validate_encoded_features(X_encoded, feature_names)

        # 9. Compute predictions & SHAP explanations
        is_classification = "claims" in dataset_type
        explainer = ModelLoader.get_explainer(dataset_type)

        results = []

        # Predict in batch for maximum efficiency
        if is_classification:
            pred_classes = model.predict(X_encoded)
            pred_probs = model.predict_proba(X_encoded)[:, 1]
        else:
            pred_premiums = model.predict(X_encoded)

        # Loop over single items in batch to fetch their respective SHAP details
        for i in range(len(X_encoded)):
            row_encoded = X_encoded.iloc[[i]]
            shap_details = explainer.explain_prediction(row_encoded)

            if is_classification:
                pred_class = int(pred_classes[i])
                pred_prob = float(pred_probs[i])
                confidence = float(np.abs(pred_prob - 0.5) * 2.0)
                
                response = {
                    "prediction_type": "claims_auto_approval",
                    "claim_prediction": bool(pred_class),
                    "approval_probability": pred_prob,
                    "confidence": confidence,
                    "top_positive_features": [
                        (item["feature_human"], item["shap_value"])
                        for item in shap_details["top_positive_contributors"][:5]
                    ],
                    "top_negative_features": [
                        (item["feature_human"], item["shap_value"])
                        for item in shap_details["top_negative_contributors"][:5]
                    ],
                    "shap_summary": shap_details["explanation_text"],
                    "timestamp": datetime.now().isoformat(),
                    "model_version": metadata.get("model_version", "1.0.0")
                }
            else:
                pred_premium = float(pred_premiums[i])
                response = {
                    "prediction_type": "premium_quotation",
                    "predicted_premium": pred_premium,
                    "currency": "INR",
                    "top_positive_features": [
                        (item["feature_human"], item["shap_value"])
                        for item in shap_details["top_positive_contributors"][:5]
                    ],
                    "top_negative_features": [
                        (item["feature_human"], item["shap_value"])
                        for item in shap_details["top_negative_contributors"][:5]
                    ],
                    "shap_summary": shap_details["explanation_text"],
                    "timestamp": datetime.now().isoformat(),
                    "model_version": metadata.get("model_version", "1.0.0")
                }
            results.append(response)

        # 10. Audit logging
        latency_ms = (time.perf_counter() - start_time) * 1000.0
        
        # Crypto hash generation (PII safe)
        input_hash = PredictionLogger.compute_input_hash(df_raw)
        pred_hash = PredictionLogger.compute_prediction_hash(results if len(results) > 1 else results[0])
        
        PredictionLogger.log_prediction(
            dataset_type=dataset_type,
            model_version=metadata.get("model_version", "1.0.0"),
            latency_ms=latency_ms,
            input_hash=input_hash,
            prediction_hash=pred_hash
        )

        return results[0] if is_single_prediction else results
