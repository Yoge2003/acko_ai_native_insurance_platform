"""
Training Pipeline Orchestrator.
Orchestrates the loading, preprocessing, feature engineering, splitting, and encoding stages.
Ensures fit operations occur strictly on training partitions to prevent data leakage.
"""

import logging
from typing import Dict, Any, Tuple
import pandas as pd

from src.ml.training.dataset_builder import DatasetBuilder
from src.ml.training.dataset_splitter import DatasetSplitter
from src.ml.training.encoding_pipeline import EncodingPipeline

# Set up logger
logger = logging.getLogger(__name__)


class TrainingPipeline:
    """
    Orchestration pipeline class for raw data preparation.
    Invokes Builder, Splitter, and Pipeline Encoders, producing machine-learning-ready datasets.
    """

    @classmethod
    def run_pipeline(cls, dataset_type: str) -> Dict[str, Any]:
        """
        Runs the end-to-end dataset preparation pipeline.

        Flow:
            1. Load and build X, y using DatasetBuilder.
            2. Split into Train/Validation/Test subsets using DatasetSplitter.
            3. Build and fit EncodingPipeline strictly on Train data.
            4. Transform Train, Validation, and Test data.
            5. Validate features consistency and shape compatibility.

        Args:
            dataset_type: one of 'car_quotation', 'bike_quotation', 'car_claims', 'bike_claims'.

        Returns:
            Dict: Prepared datasets, target arrays, fitted ColumnTransformer, and metadata.
        """
        logger.info("Initializing Training pipeline run for: %s", dataset_type)

        # 1. Build raw-feature clean dataset
        X, y, metadata = DatasetBuilder.build_dataset(dataset_type)

        # 2. Determine stratification requirement
        # Stratify only classification tasks (claims datasets)
        stratify = "claims" in dataset_type
        logger.info("Stratification mode for '%s': %s", dataset_type, stratify)

        # 3. Create Splits (70% / 15% / 15%)
        X_train, X_valid, X_test, y_train, y_valid, y_test = DatasetSplitter.split(
            X, y, stratify=stratify, random_state=42
        )

        # 4. Fit Encodersstrictly on training features
        logger.info("Setting up encoding pipeline wrapper.")
        enc_pipeline = EncodingPipeline()
        transformer = enc_pipeline.build_pipeline(X_train)

        logger.info("Fitting encoder ColumnTransformer strictly on Train Split (len=%d).", len(X_train))
        transformer.fit(X_train)
        logger.info("Fits on ColumnTransformer complete.")

        # 5. Transform all splits using fit transformer
        logger.info("Transforming datasets.")
        X_train_enc = transformer.transform(X_train)
        X_valid_enc = transformer.transform(X_valid)
        X_test_enc = transformer.transform(X_test)

        # Sanitize column names (LightGBM JSON format safety)
        X_train_enc = cls.sanitize_column_names(X_train_enc)
        X_valid_enc = cls.sanitize_column_names(X_valid_enc)
        X_test_enc = cls.sanitize_column_names(X_test_enc)

        # 6. Verify feature alignment and count constraints (Step 6 Validation)
        logger.info("--- Performing Post-Transformation Validation ---")
        
        # Verify columns align perfectly
        train_cols = X_train_enc.columns.tolist()
        valid_cols = X_valid_enc.columns.tolist()
        test_cols = X_test_enc.columns.tolist()

        if train_cols != valid_cols:
            error_msg = "Train and Validation feature column alignments do not match."
            logger.error(error_msg)
            raise ValueError(error_msg)
        if train_cols != test_cols:
            error_msg = "Train and Test feature column alignments do not match."
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        logger.info("Validation PASSED: All transformations contain identical features (count=%d).", len(train_cols))
        
        # Check for missing values in outputs
        train_nulls = X_train_enc.isna().sum().sum()
        valid_nulls = X_valid_enc.isna().sum().sum()
        test_nulls = X_test_enc.isna().sum().sum()
        
        if train_nulls > 0 or valid_nulls > 0 or test_nulls > 0:
            logger.warning(
                "Encoded datasets contain nulls after transformation. "
                "Train Nulls: %d, Valid Nulls: %d, Test Nulls: %d",
                train_nulls, valid_nulls, test_nulls
            )
        else:
            logger.info("Validation PASSED: No remaining null values in datasets.")
            
        logger.info("--- Post-Transformation Validation Complete ---")

        logger.info(
            "Training pipeline completed successfully for %s! Train size: %s, Validation size: %s, Test size: %s",
            dataset_type, X_train_enc.shape, X_valid_enc.shape, X_test_enc.shape
        )

        return {
            "X_train": X_train_enc,
            "X_val": X_valid_enc,
            "X_test": X_test_enc,
            "y_train": y_train,
            "y_val": y_valid,
            "y_test": y_test,
            "encoding_pipeline": enc_pipeline,
            "raw_metadata": metadata,
            "feature_names": train_cols,
        }

    @classmethod
    def sanitize_column_names(cls, df: pd.DataFrame) -> pd.DataFrame:
        """
        Sanitizes DataFrame column names by replacing non-alphanumeric/underscore
        characters with underscores to prevent parsing errors in LightGBM and XGBoost.
        Appends number suffixes for duplicate names to ensure uniqueness.
        """
        import re
        new_cols = []
        col_seen = {}
        for col in df.columns:
            # Replace any character other than alphanumeric or underscore with underscore
            clean_col = re.sub(r"[^a-zA-Z0-9_]", "_", str(col))
            # Collapse multiple underscores
            clean_col = re.sub(r"_+", "_", clean_col).strip("_")
            
            # De-duplicate collisions
            if clean_col in col_seen:
                col_seen[clean_col] += 1
                clean_col = f"{clean_col}_{col_seen[clean_col]}"
            else:
                col_seen[clean_col] = 1
                
            new_cols.append(clean_col)
            
        df_new = df.copy()
        df_new.columns = new_cols
        return df_new
