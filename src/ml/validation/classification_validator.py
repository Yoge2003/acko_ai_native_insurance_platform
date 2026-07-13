"""
Classification Validator Module.
Coordinates cross-validation, predictions, and misclassification error analysis for binary classifiers.
"""

import logging
from typing import Dict, Any
import pandas as pd

from src.ml.validation.cross_validation import CrossValidator
from src.ml.validation.error_analysis import ErrorAnalyzer

# Set up logger
logger = logging.getLogger(__name__)


class ClassificationValidator:
    """
    Validator to evaluate the validation stability and error profiles of binary classifiers.
    """

    def __init__(self, trainer: Any):
        """
        Initializes the ClassificationValidator.

        Args:
            trainer: CarClaimsTrainer or BikeClaimsTrainer instance.
        """
        self.trainer = trainer
        # Ensure the production model is built/available
        if self.trainer.best_model is None:
            logger.info("Initializing production model training for validator run.")
            self.trainer.train_production_model(use_full_data=True)
            self.trainer.best_model_name = "random_forest"

    def validate(self) -> Dict[str, Any]:
        """
        Evaluates the production classifier against Stratified 5-Fold CV and profiles misclassifications.

        Returns:
            Dict[str, Any]: Validation scores and error profile analysis.
        """
        logger.info("Starting classification validation sequence.")

        # Consolidate full prepared data sets for CV stability checks
        X_all = pd.concat([self.trainer.X_train, self.trainer.X_val, self.trainer.X_test], axis=0)
        y_all = pd.concat([self.trainer.y_train, self.trainer.y_val, self.trainer.y_test], axis=0)

        # 1. Run 5-Fold Stratified Cross Validation
        cv_results = CrossValidator.run_classification_cv(self.trainer.best_model, X_all, y_all, n_splits=5)

        # 2. Extract validation split predictions and probability indicators
        y_val_pred = self.trainer.best_model.predict(self.trainer.X_val)
        if hasattr(self.trainer.best_model, "predict_proba"):
            y_val_prob = self.trainer.best_model.predict_proba(self.trainer.X_val)[:, 1]
        else:
            y_val_prob = y_val_pred

        # 3. Misclassification profiling
        misclass_results = ErrorAnalyzer.analyze_classification_errors(
            self.trainer.X_val, self.trainer.y_val, y_val_pred, y_val_prob
        )

        return {
            "cv_results": cv_results,
            "misclassification_results": misclass_results,
        }
