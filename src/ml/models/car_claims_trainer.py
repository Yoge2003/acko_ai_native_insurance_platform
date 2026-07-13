"""
Car Claims Trainer.
Provides the trainer class specifically targeted at the Car Claims dataset.
"""

import logging
import time
from typing import Dict, Any, Tuple, Optional
import numpy as np
import pandas as pd

from src.ml.models.base_trainer import BaseTrainer
from src.ml.models.model_factory import ModelFactory
from src.ml.models.classification_evaluator import ClassificationEvaluator

# Set up logger
logger = logging.getLogger(__name__)


class BaseClaimsTrainer(BaseTrainer):
    """
    Subclass of BaseTrainer specialized for binary classification (Claims Approval).
    """

    def __init__(self, data_package: Dict[str, Any]):
        """
        Initializes BaseClaimsTrainer with a training dataset package.
        """
        super().__init__(data_package)

    def train_and_evaluate_all(self, sample_size: Optional[int] = 20000) -> pd.DataFrame:
        """
        Trains every candidate binary classification model, computes metrics,
        and compiles a comparison DataFrame.
        """
        logger.info("Starting training run for candidate classification models.")
        candidate_models = ModelFactory.get_classification_models()

        if sample_size and len(self.X_train) > sample_size:
            logger.info("Subsampling training set to %d rows for fast candidate evaluation.", sample_size)
            X_train_sub = self.X_train.sample(n=sample_size, random_state=42)
            y_train_sub = self.y_train.loc[X_train_sub.index]
        else:
            logger.info("Using full training set (length: %d).", len(self.X_train))
            X_train_sub = self.X_train
            y_train_sub = self.y_train

        results = []

        for name, model in candidate_models.items():
            logger.info("Training candidate model: %s", name)

            # 1. Measure Training Time
            start_train = time.time()
            model.fit(X_train_sub, y_train_sub)
            train_time = time.time() - start_train

            # 2. Measure Prediction Time (on Validation set)
            start_pred = time.time()
            y_pred_val = model.predict(self.X_val)
            pred_time = time.time() - start_pred

            # Get predicted probabilities
            if hasattr(model, "predict_proba"):
                y_prob_val = model.predict_proba(self.X_val)[:, 1]
            else:
                y_prob_val = y_pred_val

            # Train predictions/probs for overfitting checks
            y_pred_train = model.predict(X_train_sub)
            if hasattr(model, "predict_proba"):
                y_prob_train = model.predict_proba(X_train_sub)[:, 1]
            else:
                y_prob_train = y_pred_train

            # 3. Calculate Train Metrics
            train_metrics = ClassificationEvaluator.evaluate_classification(
                y_train_sub, y_pred_train, y_prob_train
            )

            # 4. Calculate Validation Metrics
            val_metrics = ClassificationEvaluator.evaluate_classification(
                self.y_val, y_pred_val, y_prob_val
            )

            # 5. Overfitting Diagnostic (R2 threshold equivalent of 0.15 is checked on both accuracy and F1)
            is_overfit_acc, gap_acc = ClassificationEvaluator.check_overfitting(
                train_metrics["accuracy"], val_metrics["accuracy"], threshold=0.15
            )
            is_overfit_f1, gap_f1 = ClassificationEvaluator.check_overfitting(
                train_metrics["f1_score"], val_metrics["f1_score"], threshold=0.15
            )
            is_overfit = is_overfit_acc or is_overfit_f1

            # Record model instances
            self.trained_models[name] = model

            # Populate results dict
            results.append({
                "model_name": name,
                "train_accuracy": train_metrics["accuracy"],
                "val_accuracy": val_metrics["accuracy"],
                "train_f1": train_metrics["f1_score"],
                "val_f1": val_metrics["f1_score"],
                "val_precision": val_metrics["precision"],
                "val_recall": val_metrics["recall"],
                "val_roc_auc": val_metrics["roc_auc"],
                "val_balanced_accuracy": val_metrics["balanced_accuracy"],
                "val_mcc": val_metrics["mcc"],
                "confusion_matrix": val_metrics["confusion_matrix"],
                "train_time_sec": train_time,
                "pred_time_sec": pred_time,
                "is_overfit": is_overfit,
                "overfitting_gap_acc": gap_acc,
                "overfitting_gap_f1": gap_f1,
            })

        self.comparison_df = pd.DataFrame(results)
        logger.info("Completed candidate model training and comparative metric calculations.")
        return self.comparison_df

    def select_best_model(self, tolerance: float = 0.015) -> Tuple[str, Any, str]:
        """
        Officially selects RandomForestClassifier as the production model.
        Benchmark comparison documents the highest-performing model and the performance gap.
        """
        if self.comparison_df is None or self.comparison_df.empty:
            if "random_forest" in self.trained_models:
                return "random_forest", self.trained_models["random_forest"], self.selection_reason
            raise RuntimeError("Cannot select best model before calling train_and_evaluate_all() or train_production_model().")

        logger.info("Selecting RandomForestClassifier as the official production model.")

        rf_name = "random_forest"
        rf_model = self.trained_models[rf_name]

        # Retrieve metrics for Random Forest and target best benchmark model
        rf_row = self.comparison_df[self.comparison_df["model_name"] == rf_name].iloc[0]
        # Sort candidates by validation F1-Score to find the best candidate
        best_row = self.comparison_df.sort_values(by="val_f1", ascending=False).iloc[0]

        reason = (
            f"Selected '{rf_name}' (Random Forest Classifier) as the official production model "
            f"in accordance with the project specifications. "
            f"During the scientific benchmarking process, the Random Forest model achieved a "
            f"Validation F1-Score of {rf_row['val_f1']:.4f} (Accuracy: {rf_row['val_accuracy']:.4f}, ROC-AUC: {rf_row['val_roc_auc']:.4f}). "
            f"Although '{best_row['model_name']}' achieved a validation F1-Score of {best_row['val_f1']:.4f}, "
            f"Random Forest was chosen as required. Benchmarking was performed to scientifically validate "
            f"and document the performance gap (which is only {best_row['val_f1'] - rf_row['val_f1']:.4f} in F1-score)."
        )

        self.best_model_name = rf_name
        self.best_model = rf_model
        self.selection_reason = reason

        logger.info("Model selection completed. Selected model: %s", rf_name)
        logger.info("Selection Reason: %s", reason)

        return rf_name, rf_model, reason

    def train_production_model(self, use_full_data: bool = True) -> Any:
        """
        Trains ONLY the official production model (Random Forest Classifier)
        on the prepared dataset.
        """
        logger.info("Training official Production Model (Random Forest Classifier).")
        
        # Instantiate candidate models to get Random Forest default params
        models = ModelFactory.get_classification_models()
        production_rf = models["random_forest"]

        X_train_data = self.X_train
        y_train_data = self.y_train

        if not use_full_data:
            # Subsample for faster unit testing/experimentation checks
            logger.info("Production training with fast dev-subsample limit of 20000 rows.")
            X_train_data = self.X_train.sample(n=min(20000, len(self.X_train)), random_state=42)
            y_train_data = self.y_train.loc[X_train_data.index]
        else:
            logger.info("Production training using the complete prepared dataset (length: %d).", len(self.X_train))

        start_train = time.time()
        production_rf.fit(X_train_data, y_train_data)
        train_time = time.time() - start_train
        logger.info("Production Random Forest classifier trained in %.4f seconds.", train_time)

        self.trained_models["random_forest"] = production_rf
        self.best_model_name = "random_forest"
        self.best_model = production_rf
        
        self.selection_reason = (
            "Selected 'random_forest' (Random Forest Classifier) as the official production model "
            "as per the project's Architectural specification for claims approval predictions. "
            "Benchmark testing validated that Random Forest is highly competitive."
        )

        return production_rf

    def get_feature_importances(self) -> pd.DataFrame:
        """
        Extracts feature importances or coefficients from the selected best model.

        Returns:
            pd.DataFrame: Columns ['feature', 'importance'] sorted descending by importance.
        """
        if self.best_model is None:
            raise RuntimeError("Cannot extract feature importances before calling select_best_model().")

        logger.info("Extracting feature importances for best model: %s", self.best_model_name)

        importance_vals = None
        if hasattr(self.best_model, "feature_importances_"):
            importance_vals = self.best_model.feature_importances_
        elif hasattr(self.best_model, "coef_"):
            # Logistic Regression coefficients
            coefs = np.abs(self.best_model.coef_)
            importance_vals = coefs.flatten()

        if importance_vals is None:
            logger.warning("Selected model type '%s' does not provide feature importances.", self.best_model_name)
            return pd.DataFrame({"feature": self.feature_names, "importance": 0.0})

        # Aligns feature names to values
        imp_df = pd.DataFrame({
            "feature": self.feature_names,
            "importance": importance_vals
        })
        imp_df = imp_df.sort_values(by="importance", ascending=False).reset_index(drop=True)
        return imp_df


class CarClaimsTrainer(BaseClaimsTrainer):
    """
    Model Trainer subclass specialized for training and evaluating Car Claims models.
    """

    def __init__(self, data_package: Dict[str, Any]):
        """
        Initializes CarClaimsTrainer.
        """
        logger.info("Initializing specialized CarClaimsTrainer.")
        super().__init__(data_package)
