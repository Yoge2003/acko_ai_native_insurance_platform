"""
Production Model Loader.
Loads models, encoders, and artifacts from disk, caching them in memory to eliminate redundant disk I/O.
"""

import os
import logging
from typing import Dict, Any, Tuple
from pathlib import Path
import joblib

from src.ml.models.model_serializer import ModelSerializer

# Set up logger
logger = logging.getLogger(__name__)


class ModelLoader:
    """
    Registry management service for cached production estimators and pipeline transformers.
    """

    _models: Dict[str, Any] = {}
    _pipelines: Dict[str, Any] = {}
    _artifacts: Dict[str, Any] = {}
    _explainers: Dict[str, Any] = {}

    MODELS_DIR = Path("src/ml/saved_models")
    PIPELINES_DIR = Path("src/ml/saved_pipelines")
    ARTIFACTS_DIR = Path("src/ml/saved_artifacts")

    @classmethod
    def load_components(cls, dataset_type: str) -> Tuple[Any, Any, Dict[str, Any]]:
        """
        Loads and caches model components for the specified dataset.

        Args:
            dataset_type: Code key of dataset ('car_quotation', etc.).

        Returns:
            Tuple[Any, Any, Dict[str, Any]]: (fitted_estimator, fitted_transformer, artifact_package)
        """
        # Ensure directories exist
        cls.MODELS_DIR.mkdir(parents=True, exist_ok=True)
        cls.PIPELINES_DIR.mkdir(parents=True, exist_ok=True)
        cls.ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

        if dataset_type not in cls._models:
            model_path = cls.MODELS_DIR / f"{dataset_type}_model.joblib"
            pipe_path = cls.PIPELINES_DIR / f"{dataset_type}_pipeline.joblib"
            art_path = cls.ARTIFACTS_DIR / f"{dataset_type}_artifacts.joblib"

            if not model_path.exists() or not pipe_path.exists() or not art_path.exists():
                logger.warning(
                    "Production assets for '%s' missing on disk. Materializing estimators dynamically...",
                    dataset_type
                )
                cls._materialize_assets(dataset_type)

            logger.info("Deserializing model components from production storage for: %s", dataset_type)
            cls._models[dataset_type] = ModelSerializer.deserialize(model_path)
            cls._pipelines[dataset_type] = joblib.load(pipe_path)
            cls._artifacts[dataset_type] = joblib.load(art_path)

        return cls._models[dataset_type], cls._pipelines[dataset_type], cls._artifacts[dataset_type]

    @classmethod
    def get_explainer(cls, dataset_type: str) -> Any:
        """
        Retrieves or instantiates a cached explainer object for the dataset.
        """
        if dataset_type not in cls._explainers:
            # Ensure components are loaded and cached first
            cls.load_components(dataset_type)

            from src.ml.explainability.quotation_explainer import QuotationExplainer
            from src.ml.explainability.claims_explainer import ClaimsExplainer

            model_path = cls.MODELS_DIR / f"{dataset_type}_model.joblib"

            logger.info("Instantiating and caching local explainer for: %s", dataset_type)
            if "claims" in dataset_type:
                cls._explainers[dataset_type] = ClaimsExplainer(dataset_type, model_path=str(model_path))
            else:
                cls._explainers[dataset_type] = QuotationExplainer(dataset_type, model_path=str(model_path))

        return cls._explainers[dataset_type]

    @classmethod
    def _materialize_assets(cls, dataset_type: str) -> None:
        """
        Trains and stores production estimators and preprocessing artifacts on disk.
        """
        logger.info("Triggering training sequence to build production assets for: %s", dataset_type)
        from src.ml.training.training_pipeline import TrainingPipeline
        from src.ml.models.car_quotation_trainer import CarQuotationTrainer
        from src.ml.models.bike_quotation_trainer import BikeQuotationTrainer
        from src.ml.models.car_claims_trainer import CarClaimsTrainer
        from src.ml.models.bike_claims_trainer import BikeClaimsTrainer
        from src.ml.training.artifact_manager import ArtifactManager

        # Run data pipeline
        data_pkg = TrainingPipeline.run_pipeline(dataset_type)

        # Train Random Forest production model
        if dataset_type == "car_quotation":
            trainer = CarQuotationTrainer(data_pkg)
        elif dataset_type == "bike_quotation":
            trainer = BikeQuotationTrainer(data_pkg)
        elif dataset_type == "car_claims":
            trainer = CarClaimsTrainer(data_pkg)
        elif dataset_type == "bike_claims":
            trainer = BikeClaimsTrainer(data_pkg)
        else:
            raise ValueError(f"Unknown dataset type: {dataset_type}")

        model = trainer.train_production_model(use_full_data=True)

        model_path = cls.MODELS_DIR / f"{dataset_type}_model.joblib"
        pipe_path = cls.PIPELINES_DIR / f"{dataset_type}_pipeline.joblib"

        # Save model and transformer pipeline
        ModelSerializer.serialize(model, model_path)
        joblib.dump(data_pkg["encoding_pipeline"].transformer, pipe_path)

        # Save artifacts
        target_name = "claim_approved" if "claims" in dataset_type else "annual_premium"
        ArtifactManager.save_artifacts(
            dataset_type=dataset_type,
            transformer=data_pkg["encoding_pipeline"].transformer,
            feature_names=data_pkg["feature_names"],
            target_name=target_name,
            raw_metadata=data_pkg["raw_metadata"],
            X_train=data_pkg["X_train"],
            y_train=data_pkg["y_train"],
            custom_dir=str(cls.ARTIFACTS_DIR)
        )
        logger.info("Production assets initialized and saved for: %s", dataset_type)
