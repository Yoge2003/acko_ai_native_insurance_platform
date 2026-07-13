"""
Regression Validator Module.
Coordinates cross-validation, prediction, and residual analysis for regression estimators as validation runs.
"""

import logging
from typing import Dict, Any
import pandas as pd
from sklearn.metrics import r2_score

from src.ml.validation.cross_validation import CrossValidator
from src.ml.validation.error_analysis import ErrorAnalyzer

# Set up logger
logger = logging.getLogger(__name__)


class RegressionValidator:
    """
    Validator to evaluate the generalization performance and residual distribution of regression estimators.
    """

    def __init__(self, trainer: Any):
        """
        Initializes the RegressionValidator.

        Args:
            trainer: CarQuotationTrainer or BikeQuotationTrainer instance.
        """
        self.trainer = trainer
        # Ensure the production model is built/available
        if self.trainer.best_model is None:
            logger.info("Initializing production model training for validator run.")
            self.trainer.train_production_model(use_full_data=True)
            self.trainer.best_model_name = "random_forest"

    def validate(self, output_dir: str, prefix: str) -> Dict[str, Any]:
        """
        Evaluates the production model against 5-Fold CV and generates residual diagnostics.

        Args:
            output_dir: Folder pathway to save matplotlib plots.
            prefix: Prefix identifier for file name tags.

        Returns:
            Dict[str, Any]: Evaluated parameters metadata.
        """
        logger.info("Starting regression validation sequence for: %s", prefix)
        
        # Consolidate full prepared data sets for 5-Fold cross-validation stability checks
        X_all = pd.concat([self.trainer.X_train, self.trainer.X_val, self.trainer.X_test], axis=0)
        y_all = pd.concat([self.trainer.y_train, self.trainer.y_val, self.trainer.y_test], axis=0)

        # 1. Run 5-Fold Cross Validation
        cv_results = CrossValidator.run_regression_cv(self.trainer.best_model, X_all, y_all, n_splits=5)

        # 2. Get predictions and compute residuals on validation split
        y_val_pred = self.trainer.best_model.predict(self.trainer.X_val)
        residual_results = ErrorAnalyzer.analyze_regression_residuals(
            self.trainer.y_val, y_val_pred, output_dir, prefix
        )

        # 3. Calculate Train/Validation Generalization Gap
        y_train_pred = self.trainer.best_model.predict(self.trainer.X_train)
        train_r2 = float(r2_score(self.trainer.y_train, y_train_pred))
        val_r2 = float(r2_score(self.trainer.y_val, y_val_pred))
        generalization_gap = train_r2 - val_r2

        logger.info(
            "Validation completed for %s. R^2 Train: %.4f, R^2 Val: %.4f, Gap: %.4f",
            prefix,
            train_r2,
            val_r2,
            generalization_gap,
        )

        return {
            "cv_results": cv_results,
            "residual_results": residual_results,
            "train_r2": train_r2,
            "val_r2": val_r2,
            "generalization_gap": generalization_gap,
        }
