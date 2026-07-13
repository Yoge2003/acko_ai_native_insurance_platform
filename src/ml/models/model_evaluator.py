"""
Model Evaluator.
Calculates performance metrics for regression tasks and diagnoses overfitting flags.
"""

import logging
from typing import Dict, Tuple
import numpy as np
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
    mean_absolute_percentage_error,
)

# Set up logger
logger = logging.getLogger(__name__)


class ModelEvaluator:
    """
    Evaluator helper class for evaluating regression metrics and evaluating overfitting markers.
    """

    @staticmethod
    def evaluate_regression(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
        """
        Calculates MAE, RMSE, R2, and MAPE metrics.

        Args:
            y_true: True ground truth values.
            y_pred: Predicted values.

        Returns:
            Dict[str, float]: Compiled performance metrics.
        """
        # Ensure numpy arrays for indexing/operations
        y_true_arr = np.array(y_true)
        y_pred_arr = np.array(y_pred)

        # MAE
        mae = float(mean_absolute_error(y_true_arr, y_pred_arr))
        
        # RMSE
        mse = mean_squared_error(y_true_arr, y_pred_arr)
        rmse = float(np.sqrt(mse))
        
        # R2
        r2 = float(r2_score(y_true_arr, y_pred_arr))
        
        # MAPE
        try:
            mape = float(mean_absolute_percentage_error(y_true_arr, y_pred_arr))
        except Exception:
            # Fallback if zero values are somehow present
            logger.warning("Could not calculate standard sklearn MAPE. Applying epsilon protection.")
            epsilon = 1e-5
            mape = float(np.mean(np.abs((y_true_arr - y_pred_arr) / np.clip(np.abs(y_true_arr), epsilon, None))))

        return {
            "R2": r2,
            "RMSE": rmse,
            "MAE": mae,
            "MAPE": mape,
        }

    @staticmethod
    def check_overfitting(train_r2: float, val_r2: float, threshold: float = 0.15) -> Tuple[bool, float]:
        """
        Diagnoses whether a model has overfit the training splits.

        Args:
            train_r2: R2 score on training data.
            val_r2: R2 score on validation data.
            threshold: Acceptable difference before marking as overfit.

        Returns:
            Tuple[bool, float]: (is_overfit, gap)
        """
        gap = train_r2 - val_r2
        is_overfit = gap > threshold
        if is_overfit:
            logger.warning("Overfitting alert! Train R^2 is %.4f while Val R^2 is %.4f (Gap = %.4f)", train_r2, val_r2, gap)
        return is_overfit, gap
