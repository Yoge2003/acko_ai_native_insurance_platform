"""
Pipeline Validator.
Validates input data schemas, version compatibility, and feature order alignment.
"""

import logging
from typing import List, Dict, Any
import pandas as pd

# Set up logger
logger = logging.getLogger(__name__)


class PipelineValidationError(Exception):
    """
    Subclass Exception thrown during validation failures within the inference pipeline.
    """
    pass


class PipelineValidator:
    """
    Inference input validator ensuring feature schemas align with trained model signatures.
    """

    @staticmethod
    def validate_raw_input(
        df_raw: pd.DataFrame,
        expected_raw_features: List[str],
        artifact_metadata: Dict[str, Any]
    ) -> None:
        """
        Validates that the raw incoming input structure conforms to expected base attributes.

        Args:
            df_raw: Raw input DataFrame matching schema.
            expected_raw_features: Expected list of base columns.
            artifact_metadata: Metadata dict containing model version configurations.
        """
        input_cols = list(df_raw.columns)

        # 1. Missing columns validation
        missing_cols = [col for col in expected_raw_features if col not in input_cols]
        if missing_cols:
            raise PipelineValidationError(
                f"Missing required columns in input DataFrame: {missing_cols}"
            )

        # 2. Unexpected columns validation
        unexpected_cols = [col for col in input_cols if col not in expected_raw_features]
        if unexpected_cols:
            raise PipelineValidationError(
                f"Unexpected columns found in input DataFrame: {unexpected_cols}. "
                f"Expected: {expected_raw_features}"
            )

        # 3. Model version compatibility
        model_version = artifact_metadata.get("model_version", "1.0.0")
        if not model_version or not isinstance(model_version, str):
            raise PipelineValidationError(
                "Model version in artifact metadata is invalid or missing."
            )

    @staticmethod
    def validate_encoded_features(
        X_encoded: pd.DataFrame,
        expected_features: List[str]
    ) -> None:
        """
        Validates the preprocessed and encoded feature matrix prior to Random Forest prediction.

        Args:
            X_encoded: Encoded feature matrix.
            expected_features: Strict list of feature names used during training.
        """
        encoded_cols = list(X_encoded.columns)

        # 1. Check feature count
        if len(encoded_cols) != len(expected_features):
            raise PipelineValidationError(
                f"Feature count mismatch: got {len(encoded_cols)} features, "
                f"expected {len(expected_features)}."
            )

        # 2. Check feature ordering
        if encoded_cols != expected_features:
            raise PipelineValidationError(
                "Feature ordering mismatch in encoded matrix. "
                "Inputs must align to training columns."
            )
