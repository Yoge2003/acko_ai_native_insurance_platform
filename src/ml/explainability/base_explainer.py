"""
Base Explainer.
Prepares datasets, verifies column orderings, loads model serialization paths, and defines explainability APIs.
"""

import os
import logging
from typing import Dict, Any, List, Optional
import pandas as pd
from abc import ABC, abstractmethod

from src.ml.models.model_serializer import ModelSerializer
from src.ml.training.training_pipeline import TrainingPipeline
from src.ml.explainability.shap_explainer import ShapExplainerWrapper

# Set up logger
logger = logging.getLogger(__name__)


class BaseExplainer(ABC):
    """
    Abstract Base Class for managing model predictions and SHAP explainability engines.
    """

    def __init__(self, dataset_type: str, model_path: Optional[str] = None):
        """
        Initializes the explainer.

        Args:
            dataset_type: Code key of dataset ('car_quotation', etc.).
            model_path: Optional file path to joblib model.
        """
        self.dataset_type = dataset_type
        self.model_path = model_path
        self.model = None
        self.feature_names = []
        self.data_package = None

        self._load_components()

    def _load_components(self) -> None:
        """
        Loads preprocessor artifacts and model parameters.
        """
        logger.info("Initializing components for explainer: %s", self.dataset_type)
        self.data_package = TrainingPipeline.run_pipeline(self.dataset_type)
        self.feature_names = self.data_package["feature_names"]

        if self.model_path and os.path.exists(self.model_path):
            logger.info("Loading serialized production model from: %s", self.model_path)
            self.model = ModelSerializer.deserialize(self.model_path)
        else:
            logger.info("No model serialization found. Training production model in memory...")
            from src.ml.models.car_quotation_trainer import CarQuotationTrainer
            from src.ml.models.bike_quotation_trainer import BikeQuotationTrainer
            from src.ml.models.car_claims_trainer import CarClaimsTrainer
            from src.ml.models.bike_claims_trainer import BikeClaimsTrainer

            if self.dataset_type == "car_quotation":
                trainer = CarQuotationTrainer(self.data_package)
            elif self.dataset_type == "bike_quotation":
                trainer = BikeQuotationTrainer(self.data_package)
            elif self.dataset_type == "car_claims":
                trainer = CarClaimsTrainer(self.data_package)
            elif self.dataset_type == "bike_claims":
                trainer = BikeClaimsTrainer(self.data_package)
            else:
                raise ValueError(f"Unknown dataset_type: {self.dataset_type}")

            self.model = trainer.train_production_model(use_full_data=True)

        self._validate_features()

    def _validate_features(self) -> None:
        """
        Verifies that columns in train, validation, and test splits align with feature names.
        """
        X_train_cols = self.data_package["X_train"].columns.tolist()
        if X_train_cols != self.feature_names:
            logger.warning("Feature alignment discrepancy found. Reordering columns to match feature_names.")
            self.data_package["X_train"] = self.data_package["X_train"][self.feature_names]
            self.data_package["X_val"] = self.data_package["X_val"][self.feature_names]
            self.data_package["X_test"] = self.data_package["X_test"][self.feature_names]

    @property
    def explainer(self) -> Any:
        """
        Calculates and caches the TreeExplainer object.
        """
        # Load explainer via wrapper
        return ShapExplainerWrapper.get_explainer(self.dataset_type, self.model)

    @abstractmethod
    def explain_prediction(self, X_input: pd.DataFrame) -> Dict[str, Any]:
        """
        Generates local explanations for a given input row.
        """
        pass

    @abstractmethod
    def explain_global(self, max_samples: int = 500) -> Dict[str, Any]:
        """
        Generates global SHAP importance ranks and profiles over sample datasets.
        """
        pass

    @abstractmethod
    def save_visualizations(self, X_input: pd.DataFrame, output_dir: str, prefix: str) -> List[str]:
        """
        Generates and saves visual plots (summary, waterfall, force, dependence, decision).
        """
        pass

    @abstractmethod
    def generate_report(self, output_path: str) -> None:
        """
        Compiles the results into a markdown explainability report.
        """
        pass
