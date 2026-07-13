"""
Car Claims Feature Engineer.
Applies domain-specific feature engineering rules for the car claims dataset.
"""

import logging
import numpy as np
import pandas as pd
from typing import List
from src.ml.feature_engineering.base_feature_engineer import BaseFeatureEngineer

# Set up logger
logger = logging.getLogger(__name__)


class CarClaimsFeatureEngineer(BaseFeatureEngineer):
    """
    Feature Engineer for the Car Claims dataset (Target variable: claim_approved).
    Engineers affected parts, financial claim ratios, early claims flags, and monsoon accident checks.
    """

    KNOWN_PARTS = [
        "bumper",
        "windshield",
        "headlight",
        "hood",
        "engine",
        "radiator",
        "door_panel",
        "alloy_wheel",
        "side_mirror",
        "dashboard",
        "taillight",
        "axle",
        "fuel_tank",
    ]

    REQUIRED_INPUT_COLS = [
        "customer_age",
        "city_tier",
        "city_risk_score",
        "vehicle_model",
        "segment",
        "engine_cc",
        "idv",
        "policy_age_months",
        "previous_claims_count",
        "ncb_at_claim_percent",
        "zero_dep_addon",
        "engine_protection_addon",
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
    ]

    def fit_transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Transforms the preprocessed Car Claims DataFrame by calculating engineered features.

        Args:
            df: Cleaned preprocessed DataFrame.

        Returns:
            pd.DataFrame: DataFrame copy with new columns added.
        """
        logger.info("Starting feature engineering for Car Claims.")
        self.validate_dataframe(df, self.REQUIRED_INPUT_COLS)
        df_feats = df.copy()

        # 1. EV handling flag
        logger.info("Engineering EV indicator flag.")
        if "engine_cc" in df_feats.columns:
            df_feats["is_electric"] = self.create_flag(df_feats["engine_cc"] == 0)
        else:
            df_feats["is_electric"] = np.int8(0)

        # 2. Extract temporal day feature from incident_date and drop raw column
        logger.info("Engineering incident day from date.")
        if "incident_date" in df_feats.columns:
            df_feats["incident_day"] = self.extract_day(df_feats["incident_date"])
            df_feats = df_feats.drop(columns=["incident_date"])
        else:
            df_feats["incident_day"] = 15

        # 3. Affected Parts Binarization
        logger.info("Engineering binarized parts indicators.")
        
        def parse_parts(val):
            if pd.isna(val) or val == "No Parts" or val == "None" or val == "no_parts":
                return []
            return [x.strip().lower().replace(" ", "_") for x in str(val).split(",")]

        parsed_parts = df_feats["affected_parts"].apply(parse_parts) if "affected_parts" in df_feats.columns else pd.Series([[]]*len(df_feats))

        df_feats["affected_parts_count"] = parsed_parts.apply(len).astype(np.int32)

        for part in self.KNOWN_PARTS:
            col_name = "part_" + part
            df_feats[col_name] = parsed_parts.apply(
                lambda lst: np.int8(1) if part in lst else np.int8(0)
            )

        if "affected_parts" in df_feats.columns:
            df_feats = df_feats.drop(columns=["affected_parts"])

        # 4. Claim to IDV ratio
        logger.info("Engineering claim to IDV ratio.")
        if "claim_amount" in df_feats.columns and "idv" in df_feats.columns:
            df_feats["claim_to_idv_ratio"] = self.safe_divide(df_feats["claim_amount"], df_feats["idv"], fill_value=0.0)
        else:
            df_feats["claim_to_idv_ratio"] = 0.0

        # 5. Early Claim Flag (policy_age_months <= 2)
        logger.info("Engineering early claim flag.")
        if "policy_age_months" in df_feats.columns:
            df_feats["early_claim_flag"] = self.create_flag(df_feats["policy_age_months"] <= 2)
        else:
            df_feats["early_claim_flag"] = np.int8(0)

        # 6. Severity Index (ratio * part count)
        logger.info("Engineering claim severity index.")
        df_feats["severity_index"] = (df_feats["claim_to_idv_ratio"] * df_feats["affected_parts_count"]).astype(np.float64)

        # 7. Monsoon Flood Match (Flooding + Jun-Sep)
        logger.info("Engineering monsoon flood flag.")
        if "incident_type" in df_feats.columns and "incident_month" in df_feats.columns:
            is_flood = df_feats["incident_type"].str.lower().fillna("") == "flooding"
            is_monsoon = df_feats["incident_month"].isin([6, 7, 8, 9])
            df_feats["monsoon_flood_match"] = self.create_flag(is_flood & is_monsoon)
        else:
            df_feats["monsoon_flood_match"] = np.int8(0)

        # 8. Incident Is Weekend
        logger.info("Engineering incident weekend flag.")
        if "incident_day_of_week" in df_feats.columns:
            df_feats["incident_is_weekend"] = self.create_flag(
                df_feats["incident_day_of_week"].str.lower().isin(["saturday", "sunday"])
            )
        else:
            df_feats["incident_is_weekend"] = np.int8(0)

        # 9. Repeat Claimant Flag (prev claims count >= 3)
        logger.info("Engineering repeat claimant flag.")
        if "previous_claims_count" in df_feats.columns:
            df_feats["repeat_claimant_flag"] = self.create_flag(df_feats["previous_claims_count"] >= 3)
        else:
            df_feats["repeat_claimant_flag"] = np.int8(0)

        # 10. Addon Coverage Match
        logger.info("Engineering addon coverage match flag.")
        if "damage_type" in df_feats.columns and "engine_protection_addon" in df_feats.columns:
            is_engine_damage = df_feats["damage_type"].str.lower().fillna("") == "engine"
            has_prot = df_feats["engine_protection_addon"] == 1
            df_feats["addon_coverage_match"] = self.create_flag(is_engine_damage & has_prot)
        else:
            df_feats["addon_coverage_match"] = np.int8(0)

        # 11. Severity Claim Ratio
        logger.info("Engineering severity claim ratio feature.")
        if "claim_amount" in df_feats.columns and "damage_severity_score" in df_feats.columns:
            denom = df_feats["damage_severity_score"] * 100000.0
            df_feats["severity_claim_ratio"] = self.safe_divide(df_feats["claim_amount"], denom, fill_value=0.0)
        else:
            df_feats["severity_claim_ratio"] = 0.0

        # Cast newly engineered float columns to float64
        float_cols = ["claim_to_idv_ratio", "severity_index", "severity_claim_ratio"]
        for col in float_cols:
            if col in df_feats.columns:
                df_feats[col] = df_feats[col].astype(np.float64)

        logger.info("Car Claims feature engineering completed. Shape: %s", df_feats.shape)
        return df_feats
