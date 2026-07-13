"""
Bike Quotation Preprocessor.
Implements the approved preprocessing strategy for the bike quotation dataset.
"""

import logging
from typing import List
import numpy as np
import pandas as pd
from src.ml.preprocessing.base_preprocessor import BasePreprocessor

# Set up logger
logger = logging.getLogger(__name__)


class BikeQuotationPreprocessor(BasePreprocessor):
    """
    Preprocessor for the Bike Quotation dataset.
    """

    REQUIRED_COLS = [
        "record_id",
        "customer_age",
        "city",
        "state",
        "city_tier",
        "city_risk_score",
        "vehicle_make",
        "vehicle_model",
        "variant",
        "segment",
        "fuel_type",
        "colour",
        "manufacturing_year",
        "vehicle_age_years",
        "engine_cc",
        "idv",
        "ncb_percent",
        "claim_history_count",
        "policy_type",
        "usage_type",
        "num_addons",
        "addons_list",
        "od_premium_before_ncb",
        "ncb_discount_amount",
        "tp_premium",
        "addon_premium",
        "gst_amount",
    ]

    LEAKAGE_COLS = [
        "od_premium_before_ncb",
        "ncb_discount_amount",
        "tp_premium",
        "addon_premium",
        "gst_amount",
    ]

    IDENTIFIER_COLS = [
        "record_id",
        "manufacturing_year",
        "colour",
    ]

    def __init__(self):
        """
        Initializes BikeQuotationPreprocessor.
        """
        super().__init__(self.REQUIRED_COLS)

    def preprocess(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Applies end-to-end preprocessing strategy for the Bike Quotation dataset.

        Args:
            df: Raw input DataFrame.

        Returns:
            pd.DataFrame: Preprocessed DataFrame copy ready for feature engineering transformer.
        """
        logger.info("Initializing preprocessing for Bike Quotation.")
        
        # 1. Standardize columns
        df_clean = self.standardize_column_names(df)

        # 2. Basic validation
        self.validate_dataframe(df_clean)
        self.check_required_columns(df_clean)

        # 3. Duplicate row check
        df_clean = self.remove_duplicates(df_clean)

        # 4. Target Leakage and Identifier Removal FIRST
        cols_to_drop = self.LEAKAGE_COLS + self.IDENTIFIER_COLS
        df_clean = self.drop_columns(df_clean, cols_to_drop)

        # 5. Handle missing values
        logger.info("Handling missing values.")
        if "addons_list" in df_clean.columns:
            df_clean["addons_list"] = df_clean["addons_list"].fillna("No Addons")

        # 6. Force categorization / type casting
        logger.info("Casting column data types.")
        categorical_cols = [
            "policy_type",
            "fuel_type",
            "segment",
            "vehicle_make",
            "state",
            "city",
            "vehicle_model",
            "variant",
            "usage_type"
        ]
        
        for col in categorical_cols:
            if col in df_clean.columns:
                df_clean[col] = df_clean[col].astype("category")

        # Cast boolean / ints
        int_cols = ["customer_age", "city_tier", "vehicle_age_years", "claim_history_count", "num_addons"]
        for col in int_cols:
            if col in df_clean.columns:
                df_clean[col] = pd.to_numeric(df_clean[col], errors="coerce").fillna(0).astype(np.int32)

        float_cols = ["city_risk_score", "idv", "ncb_percent", "engine_cc"]
        for col in float_cols:
            if col in df_clean.columns:
                df_clean[col] = pd.to_numeric(df_clean[col], errors="coerce").fillna(0.0).astype(np.float64)

        if "annual_premium" in df_clean.columns:
            df_clean["annual_premium"] = pd.to_numeric(df_clean["annual_premium"], errors="coerce").fillna(0.0).astype(np.float64)

        logger.info("Bike Quotation preprocessing complete. Preprocessed shape: %s", df_clean.shape)
        return df_clean
