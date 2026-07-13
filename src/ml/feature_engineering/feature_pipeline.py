"""
Feature Pipeline.
Functions to coordinate dataset preprocessing and feature engineering.
"""

import logging
import pandas as pd
from typing import Dict, Type

from src.ml.preprocessing.car_quotation_preprocessor import CarQuotationPreprocessor
from src.ml.preprocessing.bike_quotation_preprocessor import BikeQuotationPreprocessor
from src.ml.preprocessing.car_claims_preprocessor import CarClaimsPreprocessor
from src.ml.preprocessing.bike_claims_preprocessor import BikeClaimsPreprocessor

from src.ml.feature_engineering.car_quotation_features import CarQuotationFeatureEngineer
from src.ml.feature_engineering.bike_quotation_features import BikeQuotationFeatureEngineer
from src.ml.feature_engineering.car_claims_features import CarClaimsFeatureEngineer
from src.ml.feature_engineering.bike_claims_features import BikeClaimsFeatureEngineer

# Set up logger
logger = logging.getLogger(__name__)

# Pipelines mapper
PIPELINE_MAP: Dict[str, Dict[str, Type]] = {
    "car_quotation": {
        "preprocessor": CarQuotationPreprocessor,
        "engineer": CarQuotationFeatureEngineer,
    },
    "bike_quotation": {
        "preprocessor": BikeQuotationPreprocessor,
        "engineer": BikeQuotationFeatureEngineer,
    },
    "car_claims": {
        "preprocessor": CarClaimsPreprocessor,
        "engineer": CarClaimsFeatureEngineer,
    },
    "bike_claims": {
        "preprocessor": BikeClaimsPreprocessor,
        "engineer": BikeClaimsFeatureEngineer,
    },
}


def run_feature_pipeline(df: pd.DataFrame, dataset_type: str) -> pd.DataFrame:
    """
    Coordinates end-to-end execution:
    Raw Dataset -> Preprocessor -> Feature Engineer -> Clean Feature DataFrame.
    Does NOT scale, encode or fit scikit-learn models.

    Args:
        df: Raw input DataFrame matching the dataset schema.
        dataset_type: Key name inside PIPELINE_MAP ('car_quotation', etc.).

    Returns:
        pd.DataFrame: Engineered feature DataFrame.

    Raises:
        ValueError: If dataset_type is unknown or invalid.
    """
    logger.info("Executing feature pipeline for dataset type: %s", dataset_type)
    if dataset_type not in PIPELINE_MAP:
        error_msg = f"Unknown dataset_type '{dataset_type}'. Allowed types: {list(PIPELINE_MAP.keys())}"
        logger.error(error_msg)
        raise ValueError(error_msg)

    # 1. Instantiate modules
    preproc_class = PIPELINE_MAP[dataset_type]["preprocessor"]
    engineer_class = PIPELINE_MAP[dataset_type]["engineer"]

    preprocessor = preproc_class()
    engineer = len_params = engineer_class()

    # 2. Preprocess raw data
    logger.info("Step 1: Running Preprocessor.")
    df_preprocessed = preprocessor.preprocess(df)

    # 3. Apply Feature Engineering
    logger.info("Step 2: Running Feature Engineer.")
    df_engineered = engineer.fit_transform(df_preprocessed)

    logger.info("Feature pipeline execution complete. Final Shape: %s", df_engineered.shape)
    return df_engineered
