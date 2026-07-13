"""
Training Dataset Builder.
Handles loading raw datasets, coordinating preprocessors and feature engineers,
separating features and targets, and executing validation steps.
"""

import logging
from typing import Any, Dict, Tuple
import numpy as np
import pandas as pd

from src.ml.preprocessing.data_loader import DataLoader
from src.ml.feature_engineering.feature_pipeline import run_feature_pipeline

# Set up logger
logger = logging.getLogger(__name__)


class DatasetBuilder:
    """
    Builder class for preparing machine learning datasets.
    Loads raw CSV files, applies transformations, extracts targets, and validates formats.
    """

    FILE_MAP = {
        "car_quotation": "acko_car_quotation.csv",
        "bike_quotation": "acko_bike_quotation.csv",
        "car_claims": "acko_car_claims.csv",
        "bike_claims": "acko_bike_claims.csv",
    }

    TARGET_MAP = {
        "car_quotation": "annual_premium",
        "bike_quotation": "annual_premium",
        "car_claims": "claim_approved",
        "bike_claims": "claim_approved",
    }

    LEAKAGE_MAP = {
        "car_quotation": ["od_premium_before_ncb", "ncb_discount_amount", "tp_premium", "addon_premium", "gst_amount"],
        "bike_quotation": ["od_premium_before_ncb", "ncb_discount_amount", "tp_premium", "addon_premium", "gst_amount"],
        "car_claims": ["approval_probability"],
        "bike_claims": ["approval_probability"],
    }

    @classmethod
    def build_dataset(cls, dataset_type: str) -> Tuple[pd.DataFrame, pd.Series, Dict[str, Any]]:
        """
        Loads raw data, executes preprocessing / feature engineering pipeline,
        and splits features from the target variable with validation.

        Args:
            dataset_type: Dataset name ('car_quotation', 'bike_quotation', 'car_claims', 'bike_claims')

        Returns:
            Tuple[X (pd.DataFrame), y (pd.Series), Metadata (dict)]
        """
        logger.info("Initializing dataset build for type: %s", dataset_type)
        if dataset_type not in cls.FILE_MAP:
            raise ValueError(f"Unknown dataset_type: {dataset_type}. Supported: {list(cls.FILE_MAP.keys())}")

        filename = cls.FILE_MAP[dataset_type]
        target_col = cls.TARGET_MAP[dataset_type]

        # 1. Load Raw Data
        logger.info("Loading raw dataset: %s", filename)
        df_raw = DataLoader.load_csv(filename)
        logger.info("Raw data loaded successfully. Shape: %s", df_raw.shape)

        # Pre-pipeline duplicate column validation
        logger.info("Checking for duplicate columns in raw dataset.")
        raw_duplicate_cols = df_raw.columns[df_raw.columns.duplicated()].tolist()
        if raw_duplicate_cols:
            error_msg = f"Duplicate columns detected in raw data: {raw_duplicate_cols}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        logger.info("Validation PASSED: Raw input dataset contains no duplicate columns.")

        # 2. Run Pipeline (Preprocess -> Feature Engineering)
        logger.info("Running preprocessing and feature engineering pipeline.")
        df_engineered = run_feature_pipeline(df_raw, dataset_type)
        logger.info("Pipeline complete. Feature DF shape: %s", df_engineered.shape)

        # 3. Validation Checklist (Step 6)
        logger.info("--- Beginning Dataset Validation ---")
        
        # 3a. Target column exists
        logger.info("Validating target column: '%s'", target_col)
        if target_col not in df_engineered.columns:
            error_msg = f"Target column '{target_col}' not found in pipeline outputs."
            logger.error(error_msg)
            raise ValueError(error_msg)
        logger.info("Validation PASSED: Target column exists.")

        # 3b. No duplicate columns
        logger.info("Checking for duplicate columns in DataFrame.")
        duplicate_cols = df_engineered.columns[df_engineered.columns.duplicated()].tolist()
        if duplicate_cols:
            error_msg = f"Duplicate columns detected in pipeline output: {duplicate_cols}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        logger.info("Validation PASSED: No duplicate columns present.")

        # 3c. No missing target values
        logger.info("Validing that there are no missing values in target column.")
        missing_targets = df_engineered[target_col].isna().sum()
        if missing_targets > 0:
            logger.warning("Found %d rows with missing target values. Dropping indices.", missing_targets)
            df_engineered = df_engineered.dropna(subset=[target_col])
        logger.info("Validation PASSED: Target values complete.")

        # 3d. Check for target leakage columns in features
        leakage_cols = cls.LEAKAGE_MAP[dataset_type]
        logger.info("Checking that target leakage columns are absent: %s", leakage_cols)
        found_leakages = [col for col in leakage_cols if col in df_engineered.columns]
        if found_leakages:
            error_msg = f"Target leakage columns remaining in engineered dataset: {found_leakages}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        logger.info("Validation PASSED: No target leakage columns remaining.")
        logger.info("--- Dataset Validation Complete ---")

        # 4. Separate X and y
        y = df_engineered[target_col].copy()
        X = df_engineered.drop(columns=[target_col])

        # 5. Compile metadata
        metadata = {
            "dataset_type": dataset_type,
            "filename": filename,
            "target_column": target_col,
            "row_count": len(X),
            "feature_count": len(X.columns),
            "numeric_features": list(X.select_dtypes(include=[np.number]).columns),
            "categorical_features": list(X.select_dtypes(include=["category", "object"]).columns),
        }
        logger.info("Dataset built successfully. Rows: %d, Features: %d", len(X), len(X.columns))

        return X, y, metadata
