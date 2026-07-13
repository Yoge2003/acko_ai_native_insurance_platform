"""
Cross-Validation Module.
Runs K-Fold cross-validation for regression and Stratified K-Fold for classification.
"""

import logging
from typing import Dict, Any, List
import numpy as np
import pandas as pd
from sklearn.model_selection import KFold, StratifiedKFold
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
from sklearn.base import clone

from src.ml.models.classification_evaluator import ClassificationEvaluator

# Set up logger
logger = logging.getLogger(__name__)


class CrossValidator:
    """
    Orchestrator for managing model cross-validation processes on historical data.
    """

    @staticmethod
    def run_regression_cv(
        model: Any, X: pd.DataFrame, y: pd.Series, n_splits: int = 5
    ) -> Dict[str, Any]:
        """
        Executes standard 5-Fold Cross Validation for regression tasks.

        Args:
            model: Estimator implementing scikit-learn API.
            X: Full features DataFrame.
            y: Target Series.
            n_splits: Number of CV splits.

        Returns:
            Dict[str, Any]: Compiled validation stats.
        """
        logger.info("Initializing %d-Fold CV for regression model.", n_splits)
        kf = KFold(n_splits=n_splits, shuffle=True, random_state=42)
        r2_scores = []
        rmse_scores = []
        mae_scores = []

        X_arr = X.values
        y_arr = y.values

        for idx, (train_idx, val_idx) in enumerate(kf.split(X_arr)):
            logger.info("Evaluating regression CV Fold %d/%d.", idx + 1, n_splits)
            X_tr, X_va = X_arr[train_idx], X_arr[val_idx]
            y_tr, y_va = y_arr[train_idx], y_arr[val_idx]

            fold_model = clone(model)
            fold_model.fit(X_tr, y_tr)
            preds = fold_model.predict(X_va)

            r2_scores.append(r2_score(y_va, preds))
            rmse_scores.append(np.sqrt(mean_squared_error(y_va, preds)))
            mae_scores.append(mean_absolute_error(y_va, preds))

        summary = {
            "r2_mean": float(np.mean(r2_scores)),
            "r2_std": float(np.std(r2_scores)),
            "r2_var": float(np.var(r2_scores)),
            "rmse_mean": float(np.mean(rmse_scores)),
            "rmse_std": float(np.std(rmse_scores)),
            "mae_mean": float(np.mean(mae_scores)),
            "mae_std": float(np.std(mae_scores)),
            "raw": {
                "r2": r2_scores,
                "rmse": rmse_scores,
                "mae": mae_scores,
            },
        }
        
        logger.info("Regression CV completed. Mean R^2: %.4f (Std: %.4f)", summary["r2_mean"], summary["r2_std"])
        return summary

    @staticmethod
    def run_classification_cv(
        model: Any, X: pd.DataFrame, y: pd.Series, n_splits: int = 5
    ) -> Dict[str, Any]:
        """
        Executes Stratified 5-Fold Cross Validation for classification tasks.

        Args:
            model: Estimator implementing scikit-learn API.
            X: Full features DataFrame.
            y: Target Series.
            n_splits: Number of stratified splits.

        Returns:
            Dict[str, Any]: Compiled validation stats with standard deviations.
        """
        logger.info("Initializing %d-Fold Stratified CV for classification model.", n_splits)
        skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)
        metrics_list = []

        X_arr = X.values
        y_arr = y.values

        for idx, (train_idx, val_idx) in enumerate(skf.split(X_arr, y_arr)):
            logger.info("Evaluating classification CV Fold %d/%d.", idx + 1, n_splits)
            X_tr, X_va = X_arr[train_idx], X_arr[val_idx]
            y_tr, y_va = y_arr[train_idx], y_arr[val_idx]

            fold_model = clone(model)
            fold_model.fit(X_tr, y_tr)
            preds = fold_model.predict(X_va)

            if hasattr(fold_model, "predict_proba"):
                probs = fold_model.predict_proba(X_va)[:, 1]
            else:
                probs = preds

            fold_metrics = ClassificationEvaluator.evaluate_classification(
                y_va, preds, probs
            )
            metrics_list.append(fold_metrics)

        # Average and standard deviation calculation
        summary = {}
        metric_keys = [
            "accuracy",
            "precision",
            "recall",
            "f1_score",
            "roc_auc",
            "balanced_accuracy",
            "mcc",
        ]
        
        for key in metric_keys:
            vals = [m[key] for m in metrics_list]
            summary[f"{key}_mean"] = float(np.mean(vals))
            summary[f"{key}_std"] = float(np.std(vals))

        summary["raw"] = metrics_list
        logger.info("Classification CV completed. Mean F1: %.4f (Std: %.4f)", summary["f1_score_mean"], summary["f1_score_std"])
        return summary
