"""
Bike Quotation Feature Engineer.
Applies domain-specific feature engineering rules for the bike quotation dataset.
"""

import logging
import numpy as np
import pandas as pd
from typing import List
from src.ml.feature_engineering.base_feature_engineer import BaseFeatureEngineer

# Set up logger
logger = logging.getLogger(__name__)


class BikeQuotationFeatureEngineer(BaseFeatureEngineer):
    """
    Feature Engineer for the Bike Premium Quotation dataset.
    Extracts EV indicators, addon densities, depreciation rates, usage risk scores,
    and experienced customer metrics.
    """

    KNOWN_ADDONS = [
        "roadside_assistance",
        "consumables_cover",
        "return_to_invoice",
        "engine_protection",
        "zero_depreciation",
    ]

    REQUIRED_INPUT_COLS = [
        "customer_age",
        "city_tier",
        "city_risk_score",
        "vehicle_model",
        "segment",
        "fuel_type",
        "engine_cc",
        "idv",
        "claim_history_count",
        "usage_type",
        "num_addons",
        "addons_list",
    ]

    def fit_transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Transforms the preprocessed Bike Quotation DataFrame by calculating engineered features.

        Args:
            df: Cleaned preprocessed DataFrame.

        Returns:
            pd.DataFrame: DataFrame copy with new columns added.
        """
        logger.info("Starting feature engineering for Bike Quotation.")
        self.validate_dataframe(df, self.REQUIRED_INPUT_COLS)
        df_feats = df.copy()

        # 1. EV handling flag
        logger.info("Engineering EV indicator flag.")
        is_electric_engine = False
        is_electric_fuel = False
        if "engine_cc" in df_feats.columns:
            is_electric_engine = df_feats["engine_cc"] == 0
        if "fuel_type" in df_feats.columns:
            is_electric_fuel = df_feats["fuel_type"].str.lower() == "electric"

        df_feats["is_electric"] = self.create_flag(is_electric_engine | is_electric_fuel)

        # 2. Addon List Binarization
        logger.info("Engineering binarized addon features.")
        # Initialize binary columns to 0
        for addon_col in self.KNOWN_ADDONS:
            col_name = "addon_" + addon_col
            df_feats[col_name] = np.int8(0)

        if "addons_list" in df_feats.columns:
            def parse_addons(val):
                if pd.isna(val) or val == "No Addons" or val == "None":
                    return []
                return [x.strip().lower().replace(" ", "_") for x in str(val).split(",")]

            parsed_list = df_feats["addons_list"].apply(parse_addons)
            for addon_col in self.KNOWN_ADDONS:
                col_name = "addon_" + addon_col
                df_feats[col_name] = parsed_list.apply(
                    lambda lst: np.int8(1) if addon_col in lst else np.int8(0)
                )
            
            # Drop raw string list
            df_feats = df_feats.drop(columns=["addons_list"])

        # 3. Addon Density
        logger.info("Engineering addon density feature.")
        if "num_addons" in df_feats.columns:
            df_feats["addon_density"] = df_feats["num_addons"] / 3.0
        else:
            df_feats["addon_density"] = 0.0

        # 4. Relative Depreciation Rate
        logger.info("Engineering relative model depreciation.")
        if "idv" in df_feats.columns and "vehicle_model" in df_feats.columns:
            model_medians = df_feats.groupby("vehicle_model")["idv"].transform("median")
            df_feats["relative_depreciation"] = df_feats["idv"] / model_medians.fillna(1.0).replace(0, 1.0)
        else:
            df_feats["relative_depreciation"] = 1.0

        # 5. Usage Risk Score (exposure multiplier)
        logger.info("Engineering usage risk score.")
        if "city_risk_score" in df_feats.columns and "usage_type" in df_feats.columns:
            multipliers = {
                "personal": 1.0,
                "commercial": 1.3,
                "delivery": 1.6
            }
            multiplier_series = df_feats["usage_type"].str.lower().map(multipliers).fillna(1.0)
            df_feats["usage_risk_score"] = df_feats["city_risk_score"] * multiplier_series
        else:
            df_feats["usage_risk_score"] = df_feats["city_risk_score"] if "city_risk_score" in df_feats.columns else 1.0

        # 6. Experienced Customer Index
        logger.info("Engineering experienced customer index.")
        if "customer_age" in df_feats.columns and "claim_history_count" in df_feats.columns:
            df_feats["experienced_customer_index"] = df_feats["customer_age"] - 18 - (df_feats["claim_history_count"] * 3.0)
        else:
            df_feats["experienced_customer_index"] = 0.0

        # 7. Is Delivery EV
        logger.info("Engineering delivery EV risk flag.")
        if "usage_type" in df_feats.columns and "fuel_type" in df_feats.columns:
            is_delivery = df_feats["usage_type"].str.lower().fillna("") == "delivery"
            is_ev = df_feats["fuel_type"].str.lower().fillna("") == "electric"
            df_feats["is_delivery_ev"] = self.create_flag(is_delivery & is_ev)
        else:
            df_feats["is_delivery_ev"] = np.int8(0)

        # Force category / output type casting
        float_cols = ["addon_density", "relative_depreciation", "usage_risk_score", "experienced_customer_index"]
        for col in float_cols:
            if col in df_feats.columns:
                df_feats[col] = df_feats[col].astype(np.float64)

        logger.info("Bike Quotation feature engineering completed. Shape: %s", df_feats.shape)
        return df_feats
