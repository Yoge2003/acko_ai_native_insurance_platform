"""
Artifact Manager.
Handles saving and loading of model prep artifacts (transformers, feature names, statistics).
Uses Joblib for serialization and automatically manages artifact directories.
"""

import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional
import joblib
import pandas as pd

# Set up logger
logger = logging.getLogger(__name__)


class ArtifactManager:
    """
    Manager for serializing and deserializing data preparation artifacts.
    Standardizes directory validation, metadata version control, and data statistics storage.
    """

    DEFAULT_ARTIFACTS_DIR = Path("src/ml/artifacts")
    PROJECT_VERSION = "1.0.0"

    @classmethod
    def get_artifacts_dir(cls, custom_dir: Optional[str] = None) -> Path:
        """
        Retrieves the directory target path for artifacts and ensures it exists.

        Args:
            custom_dir: Optional custom path.

        Returns:
            Path object of the directory.
        """
        base_dir = Path(custom_dir) if custom_dir else cls.DEFAULT_ARTIFACTS_DIR
        base_dir.mkdir(parents=True, exist_ok=True)
        return base_dir

    @classmethod
    def compile_dataset_statistics(cls, X: pd.DataFrame, y: pd.Series) -> Dict[str, Any]:
        """
        Compiles descriptive overview statistics for feature monitoring.

        Args:
            X: Clean/Transformed features DataFrame.
            y: Target Series.

        Returns:
            Dict: Column-wise metrics and target balance statistics.
        """
        logger.info("Compiling dataset statistics.")
        stats = {
            "num_samples": len(X),
            "num_features": len(X.columns),
            "feature_nans": X.isna().sum().to_dict(),
        }

        # Select only numeric subset for mean/std describer
        numeric_df = X.select_dtypes(include=["number"])
        if not numeric_df.empty:
            stats["numeric_describe"] = numeric_df.describe().to_dict()

        # Calculate target distribution metrics
        if pd.api.types.is_numeric_dtype(y.dtype) and len(y.unique()) > 10:
            # Continuous target (regression)
            stats["target"] = {
                "type": "continuous",
                "mean": float(y.mean()),
                "median": float(y.median()),
                "std": float(y.std()),
                "min": float(y.min()),
                "max": float(y.max()),
            }
        else:
            # Discrete/Categorical target (classification)
            counts = y.value_counts()
            total = len(y)
            stats["target"] = {
                "type": "classification",
                "distribution": {str(k): int(v) for k, v in counts.items()},
                "ratios": {str(k): float(v) / total for k, v in counts.items()},
            }

        return stats

    @classmethod
    def save_artifacts(
        cls,
        dataset_type: str,
        transformer: Any,
        feature_names: List[str],
        target_name: str,
        raw_metadata: Dict[str, Any],
        X_train: pd.DataFrame,
        y_train: pd.Series,
        custom_dir: Optional[str] = None,
    ) -> Path:
        """
        Saves all training artifacts to a unified joblib file.

        Args:
            dataset_type: Code key of dataset ('car_quotation', etc.).
            transformer: Fitted ColumnTransformer or encoding pipeline block.
            feature_names: List of final transformed feature column names.
            target_name: Destination target name string.
            raw_metadata: Associated schema execution metadata.
            X_train: Training features DataFrame to compute baseline drift statistics.
            y_train: Training target Series.
            custom_dir: Custom saving base directory.

        Returns:
            Path: Complete path to output joblib artifact package.
        """
        dest_dir = cls.get_artifacts_dir(custom_dir)
        filepath = dest_dir / f"{dataset_type}_artifacts.joblib"
        logger.info("Saving training artifacts to: %s", filepath)

        # 1. Compile statistics
        dataset_stats = cls.compile_dataset_statistics(X_train, y_train)

        # 2. Package artifacts
        package = {
            "dataset_type": dataset_type,
            "project_version": cls.PROJECT_VERSION,
            "timestamp": pd.Timestamp.now().isoformat(),
            "transformer": transformer,
            "feature_names": feature_names,
            "target_name": target_name,
            "raw_metadata": raw_metadata,
            "dataset_statistics": dataset_stats,
        }

        # 3. Serialize to disk
        try:
            joblib.dump(package, filepath)
            logger.info("Successfully saved artifacts. joblib size: %d bytes", filepath.stat().st_size)
        except Exception as e:
            error_msg = f"Failed to serialize artifacts to {filepath}. Error: {e}"
            logger.error(error_msg)
            raise e

        return filepath

    @classmethod
    def load_artifacts(cls, dataset_type: str, custom_dir: Optional[str] = None) -> Dict[str, Any]:
        """
        Loads preparation artifacts for inference or inspection.

        Args:
            dataset_type: Code key of dataset.
            custom_dir: Custom saving base directory.

        Returns:
            Dict: Deserialized artifact package.
        """
        base_dir = Path(custom_dir) if custom_dir else cls.DEFAULT_ARTIFACTS_DIR
        filepath = base_dir / f"{dataset_type}_artifacts.joblib"
        logger.info("Loading training artifacts from: %s", filepath)

        if not filepath.exists():
            error_msg = f"Artifact file not found at: {filepath.absolute()}"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)

        try:
            package = joblib.load(filepath)
            logger.info(
                "Successfully loaded artifacts. Timestamp: %s, Project Version: %s",
                package.get("timestamp"),
                package.get("project_version"),
            )
            return package
        except Exception as e:
            error_msg = f"Failed to load artifacts from {filepath}. Error: {e}"
            logger.error(error_msg)
            raise RuntimeError(error_msg) from e
