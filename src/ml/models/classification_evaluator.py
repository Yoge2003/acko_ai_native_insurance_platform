"""
Classification Evaluator.
Calculates performance metrics for binary classification tasks and diagnoses overfitting.
"""

import logging
from typing import Dict, Any, Tuple
import numpy as np
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    balanced_accuracy_score,
    matthews_corrcoef,
    confusion_matrix,
    roc_curve,
)

# Set up logger
logger = logging.getLogger(__name__)


class ClassificationEvaluator:
    """
    Evaluator helper class for evaluating classification metrics and overfitting.
    """

    @staticmethod
    def evaluate_classification(
        y_true: np.ndarray, y_pred: np.ndarray, y_prob: np.ndarray
    ) -> Dict[str, Any]:
        """
        Calculates Accuracy, Precision, Recall, F1 Score, ROC-AUC,
        Balanced Accuracy, Matthews Correlation Coefficient (MCC), and Confusion Matrix.

        Args:
            y_true: True ground truth values.
            y_pred: Predicted label values.
            y_prob: Predicted probability values (class 1).

        Returns:
            Dict[str, Any]: Compiled performance metrics.
        """
        y_true_arr = np.array(y_true)
        y_pred_arr = np.array(y_pred)
        y_prob_arr = np.array(y_prob)

        # Accuracy
        accuracy = float(accuracy_score(y_true_arr, y_pred_arr))

        # Precision
        precision = float(precision_score(y_true_arr, y_pred_arr, zero_division=0))

        # Recall
        recall = float(recall_score(y_true_arr, y_pred_arr, zero_division=0))

        # F1 Score
        f1 = float(f1_score(y_true_arr, y_pred_arr, zero_division=0))

        # ROC-AUC
        try:
            # Check if there is only one class in y_true
            if len(np.unique(y_true_arr)) < 2:
                roc_auc = 0.5
            else:
                roc_auc = float(roc_auc_score(y_true_arr, y_prob_arr))
        except Exception as e:
            logger.warning("Could not calculate ROC-AUC: %s. Defaulting to 0.5.", e)
            roc_auc = 0.5

        # Balanced Accuracy
        balanced_acc = float(balanced_accuracy_score(y_true_arr, y_pred_arr))

        # MCC
        mcc = float(matthews_corrcoef(y_true_arr, y_pred_arr))

        # Confusion Matrix
        conf_mat = confusion_matrix(y_true_arr, y_pred_arr).tolist()

        return {
            "accuracy": accuracy,
            "precision": precision,
            "recall": recall,
            "f1_score": f1,
            "roc_auc": roc_auc,
            "balanced_accuracy": balanced_acc,
            "mcc": mcc,
            "confusion_matrix": conf_mat,
        }

    @staticmethod
    def check_overfitting(
        train_value: float, val_value: float, threshold: float = 0.15
    ) -> Tuple[bool, float]:
        """
        Diagnoses whether a model has overfit the training splits.

        Args:
            train_value: Metric evaluation on training data.
            val_value: Metric evaluation on validation data.
            threshold: Acceptable difference before marking as overfit.

        Returns:
            Tuple[bool, float]: (is_overfit, gap)
        """
        gap = train_value - val_value
        is_overfit = gap > threshold
        if is_overfit:
            logger.warning(
                "Overfitting alert! Training score (%.4f) vs Validation score (%.4f) has gap %.4f",
                train_value,
                val_value,
                gap,
            )
        return is_overfit, gap

    @staticmethod
    def get_roc_curve_data(y_true: np.ndarray, y_prob: np.ndarray) -> Dict[str, Any]:
        """
        Generates FPR, TPR, and Threshold arrays for ROC Curve display.
        """
        y_true_arr = np.array(y_true)
        y_prob_arr = np.array(y_prob)
        if len(np.unique(y_true_arr)) < 2:
            return {"fpr": [0.0, 1.0], "tpr": [0.0, 1.0], "thresholds": [1.0, 0.0]}

        fpr, tpr, thresholds = roc_curve(y_true_arr, y_prob_arr)
        return {
            "fpr": fpr.tolist(),
            "tpr": tpr.tolist(),
            "thresholds": thresholds.tolist(),
        }
