"""
Bike Claims Preprocessor.
Implements the approved preprocessing strategy for the bike claims dataset.
"""

import logging
from typing import List
import numpy as np
import pandas as pd
from src.ml.preprocessing.base_preprocessor import BasePreprocessor

# Set up logger
logger = logging.getLogger(__name__)


class BikeClaimsPreprocessor(BasePreprocessor):
    """
    Preprocessor for the Bike Claims dataset (classification target: claim_approved).
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
        "segment",
        "engine_cc",
        "manufacturing_year",
        "vehicle_age_years",
        "idv",
        "policy_type",
        "policy_age_months",
        "annual_premium_paid",
        "previous_claims_count",
        "ncb_at_claim_percent",
        "zero_dep_addon",
        "usage_type",
        "rider_experience_years",
        "helmet_worn",
        "incident_date",
        "incident_day_of_week",
        "incident_month",
        "incident_time_of_day",
        "incident_type",
        "damage_type",
        "damage_severity_score",
        "num_parts_affected",
        "affected_parts",
        "claim_amount",
        "approval_probability",
        "claim_approved",
    ]

    LEAKAGE_COLS = [
        "approval_probability",
    ]

    IDENTIFIER_COLS = [
        "record_id",
        "manufacturing_year",
    ]

    def __init__(self):
        """
        Initializes BikeClaimsPreprocessor.
        """
        super().__init__(self.REQUIRED_COLS)

    def preprocess(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Applies end-to-end preprocessing strategy for the Bike Claims dataset.

        Args:
            df: Raw input DataFrame.

        Returns:
            pd.DataFrame: Preprocessed DataFrame copy ready for feature engineering transformer.
        """
        logger.info("Initializing preprocessing for Bike Claims.")
        
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

        # 5. Fill missing values (if any)
        logger.info("Imputing missing values if present.")
        for col in ["zero_dep_addon", "previous_claims_count", "ncb_at_claim_percent", "num_parts_affected"]:
            if col in df_clean.columns:
                df_clean[col] = df_clean[col].fillna(0)

        if "helmet_worn" in df_clean.columns:
            df_clean["helmet_worn"] = df_clean["helmet_worn"].fillna(1)  # assume helmet worn as mode default

        if "rider_experience_years" in df_clean.columns:
            df_clean["rider_experience_years"] = df_clean["rider_experience_years"].fillna(df_clean["rider_experience_years"].median())

        if "incident_time_of_day" in df_clean.columns:
            df_clean["incident_time_of_day"] = df_clean["incident_time_of_day"].fillna("Unknown")

        if "damage_severity_score" in df_clean.columns:
            df_clean["damage_severity_score"] = df_clean["damage_severity_score"].fillna(df_clean["damage_severity_score"].median())

        if "affected_parts" in df_clean.columns:
            df_clean["affected_parts"] = df_clean["affected_parts"].fillna("No Parts")

        # 6. Force categorization / type casting
        logger.info("Casting column data types.")
        categorical_cols = [
            "policy_type",
            "segment",
            "vehicle_make",
            "state",
            "city",
            "vehicle_model",
            "usage_type",
            "incident_day_of_week",
            "incident_time_of_day",
            "incident_type",
            "damage_type",
        ]
        
        for col in categorical_cols:
            if col in df_clean.columns:
                df_clean[col] = df_clean[col].astype("category")

        # Cast boolean / ints
        int_cols = [
            "customer_age",
            "city_tier",
            "vehicle_age_years",
            "previous_claims_count",
            "zero_dep_addon",
            "helmet_worn",
            "incident_month",
            "num_parts_affected",
        ]
        for col in int_cols:
            if col in df_clean.columns:
                df_clean[col] = pd.to_numeric(df_clean[col], errors="coerce").fillna(0).astype(np.int32)

        float_cols = [
            "city_risk_score",
            "idv",
            "annual_premium_paid",
            "ncb_at_claim_percent",
            "rider_experience_years",
            "damage_severity_score",
            "claim_amount",
            "engine_cc",
        ]
        for col in float_cols:
            if col in df_clean.columns:
                df_clean[col] = pd.to_numeric(df_clean[col], errors="coerce").fillna(0.0).astype(np.float64)

        if "claim_approved" in df_clean.columns:
            df_clean["claim_approved"] = pd.to_numeric(df_clean["claim_approved"], errors="coerce").fillna(0).astype(np.int32)

        logger.info("Bike Claims preprocessing complete. shape: %s", df_clean.shape)
        return df_clean
