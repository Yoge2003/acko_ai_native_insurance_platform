"""
Quotation Predictor.
Exposes predict() and predict_batch() to run premium estimations with model confidence metrics.
"""

import logging
from typing import Dict, Any, List, Union
import numpy as np
import pandas as pd

from src.ml.inference.prediction_pipeline import PredictionPipeline
from src.ml.inference.model_loader import ModelLoader

# Set up logger
logger = logging.getLogger(__name__)


class QuotationPredictor:
    """
    Exposes premium quotation endpoints for Car and Bike Premium models.
    """

    def __init__(self, vehicle_type: str):
        """
        Initializes QuotationPredictor.

        Args:
            vehicle_type: Either 'car' or 'bike'.
        """
        val_type = vehicle_type.lower().strip()
        if val_type not in ["car", "bike"]:
            raise ValueError("vehicle_type must be either 'car' or 'bike'.")
        self.vehicle_type = val_type
        self.dataset_type = f"{val_type}_quotation"

    def predict(self, raw_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predicts premium for a single application request.

        Args:
            raw_input: Raw key-value input records.

        Returns:
            Dict[str, Any]: Standardized Quotation prediction response.
        """
        res = PredictionPipeline.run_inference(self.dataset_type, raw_input)
        if isinstance(res, list):
            res = res[0]

        # Inject Ensemble confidence metadata (variance of individual tree estimators)
        try:
            model, transformer, artifacts = ModelLoader.load_components(self.dataset_type)
            feature_names = artifacts.get("feature_names", [])

            # Extract sample and encode
            df_sample = pd.DataFrame([raw_input])
            
            # Standardize column headers of raw input (spaces/dashes to underscores, lowercase)
            df_sample.columns = (
                df_sample.columns.str.strip()
                .str.lower()
                .str.replace(" ", "_")
                .str.replace("-", "_")
            )

            # Fill expected columns prior to encoding
            for col in transformer.feature_names_in_:
                if col not in df_sample.columns:
                    df_sample[col] = 0

            # Transform
            X_enc_df = transformer.transform(df_sample[transformer.feature_names_in_])
            # Align features
            import re
            new_cols = [re.sub(r"[^a-zA-Z0-9_]", "_", col) for col in X_enc_df.columns]
            new_cols = [re.sub(r"_+", "_", col).strip("_") for col in new_cols]
            X_enc_df.columns = new_cols
            X_enc = X_enc_df[feature_names]

            # Compute tree predictions variance
            tree_preds = np.array([tree.predict(X_enc) for tree in model.estimators_])
            pred_std = float(np.std(tree_preds, axis=0)[0])

            res["confidence_metadata"] = {
                "ensemble_std": pred_std,
                "confidence_score": max(0.0, 1.0 - (pred_std / max(1.0, res["predicted_premium"])))
            }
        except Exception as e:
            logger.warning("Could not calculate ensemble uncertainty metric: %s", e)
            res["confidence_metadata"] = {"ensemble_std": 0.0, "confidence_score": 1.0}

        return res

    def predict_batch(self, raw_inputs: Union[List[Dict[str, Any]], pd.DataFrame]) -> List[Dict[str, Any]]:
        """
        Runs batch prediction over multiple quotation inputs in a vectorized pass.

        Args:
            raw_inputs: List of input dictionaries or pandas DataFrame.

        Returns:
            List[Dict[str, Any]]: List of standard quotation objects.
        """
        # 1. Run batch inference using prediction pipeline
        results = PredictionPipeline.run_inference(self.dataset_type, raw_inputs)
        if isinstance(results, dict):
            results = [results]

        # 2. Add ensemble standard deviations in vectorized loop
        try:
            model, transformer, artifacts = ModelLoader.load_components(self.dataset_type)
            feature_names = artifacts.get("feature_names", [])

            if isinstance(raw_inputs, pd.DataFrame):
                df_sample = raw_inputs.copy()
            else:
                df_sample = pd.DataFrame(raw_inputs)

            # Standardize names
            df_sample.columns = (
                df_sample.columns.str.strip()
                .str.lower()
                .str.replace(" ", "_")
                .str.replace("-", "_")
            )

            # Fill expected columns prior to encoding
            for col in transformer.feature_names_in_:
                if col not in df_sample.columns:
                    df_sample[col] = 0

            # Transform
            X_enc_df = transformer.transform(df_sample[transformer.feature_names_in_])
            
            # Align features name format matching sanitizations
            import re
            new_cols = [re.sub(r"[^a-zA-Z0-9_]", "_", col) for col in X_enc_df.columns]
            new_cols = [re.sub(r"_+", "_", col).strip("_") for col in new_cols]
            X_enc_df.columns = new_cols
            X_enc = X_enc_df[feature_names]

            # Compute tree predictions variance in vectorized format for all samples!
            tree_preds = np.array([tree.predict(X_enc) for tree in model.estimators_])  # shape: (num_trees, N)
            pred_stds = np.std(tree_preds, axis=0)  # shape: (N,)

            for i, res in enumerate(results):
                res["confidence_metadata"] = {
                    "ensemble_std": float(pred_stds[i]),
                    "confidence_score": float(max(0.0, 1.0 - (pred_stds[i] / max(1.0, res["predicted_premium"]))))
                }
        except Exception as e:
            logger.warning("Could not calculate ensemble uncertainty batch metrics: %s", e)
            for res in results:
                if "confidence_metadata" not in res:
                    res["confidence_metadata"] = {"ensemble_std": 0.0, "confidence_score": 1.0}

        return results
