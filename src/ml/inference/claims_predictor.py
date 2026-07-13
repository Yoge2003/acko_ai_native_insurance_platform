"""
Claims Predictor.
Exposes predict() and predict_batch() to run claims auto-approval predictions with confidence metrics.
"""

import logging
from typing import Dict, Any, List, Union
import pandas as pd

from src.ml.inference.prediction_pipeline import PredictionPipeline

# Set up logger
logger = logging.getLogger(__name__)


class ClaimsPredictor:
    """
    Exposes claims approval endpoints for Car and Bike Claims models.
    """

    def __init__(self, vehicle_type: str):
        """
        Initializes ClaimsPredictor.

        Args:
            vehicle_type: Either 'car' or 'bike'.
        """
        val_type = vehicle_type.lower().strip()
        if val_type not in ["car", "bike"]:
            raise ValueError("vehicle_type must be either 'car' or 'bike'.")
        self.vehicle_type = val_type
        self.dataset_type = f"{val_type}_claims"

    def predict(self, raw_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predicts approval for a single claims request.

        Args:
            raw_input: Raw key-value input records.

        Returns:
            Dict[str, Any]: Standardized Claims prediction response.
        """
        res = PredictionPipeline.run_inference(self.dataset_type, raw_input)
        if isinstance(res, list):
            res = res[0]
        return res

    def predict_batch(self, raw_inputs: Union[List[Dict[str, Any]], pd.DataFrame]) -> List[Dict[str, Any]]:
        """
        Runs batch prediction over multiple claim inputs in a single vectorized pass.

        Args:
            raw_inputs: List of input dictionaries or pandas DataFrame.

        Returns:
            List[Dict[str, Any]]: List of standard claims approval objects.
        """
        results = PredictionPipeline.run_inference(self.dataset_type, raw_inputs)
        if isinstance(results, dict):
            results = [results]
        return results
