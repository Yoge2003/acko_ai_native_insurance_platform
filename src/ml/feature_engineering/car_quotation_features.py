"""
Car Quotation Feature Engineer.
Applies domain-specific feature engineering rules for the car quotation dataset.
"""

import logging
import numpy as np
import pandas as pd
from typing import List
from src.ml.feature_engineering.base_feature_engineer import BaseFeatureEngineer

# Set up logger
logger = logging.getLogger(__name__)


class CarQuotationFeatureEngineer(BaseFeatureEngineer):
    """
    Feature Engineer for the Car Premium Quotation dataset.
    Extracts EV indicators, addon densities, relative depreciation rates, and driver experience indices.
    """

    KNOWN_ADDONS = [
        "Personal Accident Cover",
        "Return to Invoice",
        "Key Replacement",
        "Roadside Assistance",
        "No Claim Bonus Protection",
        "Consumables Cover",
        "Passenger Cover",
        "Zero Depreciation",
        "Tyre Protection",
        "Engine Protection",
    ]

    REQUIRED_INPUT_COLS = [
        "customer_age",
        "city_tier",
        "city_risk_score",
        "vehicle_model",
        "segment",
        "engine_cc",
        "idv",
        "claim_history_count",
        "num_addons",
        "addons_list",
    ]

    def fit_transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Transforms the preprocessed Car Quotation DataFrame by calculating engineered features.

        Args:
            df: Cleaned preprocessed DataFrame.

        Returns:
            pd.DataFrame: DataFrame copy with new columns added.
        """
        logger.info("Starting feature engineering for Car Quotation.")
        self.validate_dataframe(df, self.REQUIRED_INPUT_COLS)
        df_feats = df.copy()

        # 1. EV handling flag
        logger.info("Engineering EV indicator flag.")
        if "engine_cc" in df_feats.columns:
            df_feats["is_electric"] = self.create_flag(df_feats["engine_cc"] == 0)
        else:
            df_feats["is_electric"] = np.int8(0)

        # 2. Addon List Binarization
        logger.info("Engineering binarized addon features.")
        # Initialize binary addon columns to 0
        for addon in self.KNOWN_ADDONS:
            col_name = "addon_" + addon.lower().replace(" ", "_")
            df_feats[col_name] = np.int8(0)

        # Populate binarized features
        if "addons_list" in df_feats.columns:
            def parse_addons(val):
                if pd.isna(val) or val == "No Addons" or val == "None":
                    return []
                return [x.strip() for x in str(val).split(",")]

            parsed_list = df_feats["addons_list"].apply(parse_addons)
            for addon in self.KNOWN_ADDONS:
                col_name = "addon_" + addon.lower().replace(" ", "_")
                df_feats[col_name] = parsed_list.apply(
                    lambda lst: np.int8(1) if addon in lst else np.int8(0)
                )
            
            # Prune original text column
            df_feats = df_feats.drop(columns=["addons_list"])

        # 3. Addon Density
        logger.info("Engineering addon density feature.")
        if "num_addons" in df_feats.columns:
            df_feats["addon_density"] = df_feats["num_addons"] / 4.0
        else:
            df_feats["addon_density"] = 0.0

        # 4. Relative Depreciation Rate
        logger.info("Engineering relative model depreciation.")
        if "idv" in df_feats.columns and "vehicle_model" in df_feats.columns:
            model_medians = df_feats.groupby("vehicle_model")["idv"].transform("median")
            df_feats["relative_depreciation"] = df_feats["idv"] / model_medians.fillna(1.0).replace(0, 1.0)
        else:
            df_feats["relative_depreciation"] = 1.0

        # 5. Driver Experience Index
        logger.info("Engineering driver experience index.")
        if "customer_age" in df_feats.columns and "claim_history_count" in df_feats.columns:
            df_feats["driver_experience_index"] = df_feats["customer_age"] - 18 - df_feats["claim_history_count"]
        else:
            df_feats["driver_experience_index"] = 0.0

        # 6. EV High Risk Flag (EV + Tier 3 charging infrastructure vulnerability)
        logger.info("Engineering EV tier risk flag.")
        if "segment" in df_feats.columns and "city_tier" in df_feats.columns:
            is_ev = df_feats["segment"].str.lower().fillna("") == "ev"
            is_tier3 = df_feats["city_tier"] == 3
            df_feats["ev_high_risk_flag"] = self.create_flag(is_ev & is_tier3)
        else:
            df_feats["ev_high_risk_flag"] = np.int8(0)

        # Force datatype compliance for newly engineered features
        float_cols = ["addon_density", "relative_depreciation", "driver_experience_index"]
        for col in float_cols:
            if col in df_feats.columns:
                df_feats[col] = df_feats[col].astype(np.float64)

        logger.info("Car Quotation feature engineering completed. Shape: %s", df_feats.shape)
        return df_feats
