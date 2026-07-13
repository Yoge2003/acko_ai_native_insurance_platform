"""
Pipeline Factory.
Generates scikit-learn preprocessing pipelines for all four datasets.
"""

import logging
from typing import List, Dict, Any, Tuple
import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import (
    StandardScaler,
    MinMaxScaler,
    RobustScaler,
    OneHotEncoder,
    FunctionTransformer,
)
try:
    from sklearn.preprocessing import TargetEncoder
except ImportError:
    from category_encoders import TargetEncoder

from src.ml.feature_engineering.car_quotation_features import CarQuotationFeatureEngineer
from src.ml.feature_engineering.bike_quotation_features import BikeQuotationFeatureEngineer
from src.ml.feature_engineering.car_claims_features import CarClaimsFeatureEngineer
from src.ml.feature_engineering.bike_claims_features import BikeClaimsFeatureEngineer

# Set up logger
logger = logging.getLogger(__name__)


class PipelineFactory:
    """
    Factory class for building modular scikit-learn preprocessing pipelines.
    Supports car/bike quotation (regression) and car/bike claims (classification).
    """

    @staticmethod
    def get_feature_groups(dataset_type: str) -> Dict[str, List[str]]:
        """
        Retrieves feature groups specific to each dataset type for the ColumnTransformer.

        Args:
            dataset_type: One of 'car_quotation', 'bike_quotation', 'car_claims', 'bike_claims'.

        Returns:
            Dict[str, List[str]]: Mapping of scaler/encoder type to list of columns.
        """
        groups: Dict[str, List[str]] = {
            "robust_features": [],
            "standard_features": [],
            "minmax_features": [],
            "ohe_features": [],
            "target_features": [],
            "passthru_features": [],
        }

        if dataset_type == "car_quotation":
            groups["robust_features"] = ["idv"]
            groups["standard_features"] = ["customer_age", "engine_cc", "claim_history_count"]
            groups["minmax_features"] = ["vehicle_age_years", "ncb_percent", "num_addons"]
            groups["ohe_features"] = ["state", "segment", "fuel_type", "policy_type", "vehicle_make", "previous_insurer"]
            groups["target_features"] = ["city", "vehicle_model", "variant"]
            
            addon_cols = ["addon_" + addon.lower().replace(" ", "_") for addon in CarQuotationFeatureEngineer.KNOWN_ADDONS]
            groups["passthru_features"] = [
                "city_tier", "city_risk_score", "is_electric", "addon_density",
                "relative_depreciation", "driver_experience_index", "ev_high_risk_flag"
            ] + addon_cols

        elif dataset_type == "bike_quotation":
            groups["robust_features"] = ["idv"]
            groups["standard_features"] = ["customer_age", "engine_cc", "claim_history_count"]
            groups["minmax_features"] = ["vehicle_age_years", "ncb_percent", "num_addons"]
            groups["ohe_features"] = ["state", "segment", "fuel_type", "policy_type", "vehicle_make", "usage_type"]
            groups["target_features"] = ["city", "vehicle_model", "variant"]
            
            addon_cols = ["addon_" + addon for addon in BikeQuotationFeatureEngineer.KNOWN_ADDONS]
            groups["passthru_features"] = [
                "city_tier", "city_risk_score", "is_electric", "addon_density",
                "relative_depreciation", "usage_risk_score", "experienced_customer_index", "is_delivery_ev"
            ] + addon_cols

        elif dataset_type == "car_claims":
            groups["robust_features"] = ["idv", "claim_amount"]
            groups["standard_features"] = ["customer_age", "previous_claims_count"]
            groups["minmax_features"] = ["vehicle_age_years", "ncb_at_claim_percent", "num_parts_affected", "incident_month", "incident_day"]
            groups["ohe_features"] = ["state", "segment", "policy_type", "vehicle_make", "incident_day_of_week", "incident_time_of_day", "incident_type", "damage_type"]
            groups["target_features"] = ["city", "vehicle_model"]
            
            part_cols = ["part_" + part for part in CarClaimsFeatureEngineer.KNOWN_PARTS]
            groups["passthru_features"] = [
                "city_tier", "city_risk_score", "is_electric", "zero_dep_addon", "engine_protection_addon",
                "affected_parts_count", "claim_to_idv_ratio", "early_claim_flag", "severity_index",
                "monsoon_flood_match", "incident_is_weekend", "repeat_claimant_flag", "addon_coverage_match",
                "severity_claim_ratio"
            ] + part_cols

        elif dataset_type == "bike_claims":
            groups["robust_features"] = ["idv", "claim_amount"]
            groups["standard_features"] = ["customer_age", "previous_claims_count"]
            groups["minmax_features"] = ["vehicle_age_years", "ncb_at_claim_percent", "num_parts_affected", "incident_month", "incident_day", "rider_experience_years"]
            groups["ohe_features"] = ["state", "segment", "policy_type", "vehicle_make", "usage_type", "incident_day_of_week", "incident_time_of_day", "incident_type", "damage_type"]
            groups["target_features"] = ["city", "vehicle_model"]
            
            part_cols = ["part_" + part for part in BikeClaimsFeatureEngineer.KNOWN_PARTS]
            groups["passthru_features"] = [
                "city_tier", "city_risk_score", "is_electric", "zero_dep_addon", "helmet_worn",
                "affected_parts_count", "claim_to_idv_ratio", "early_claim_flag", "severity_index",
                "monsoon_flood_match", "incident_is_weekend", "non_helmet_injury_flag", "novice_rider_flag",
                "delivery_high_risk_flag", "experienced_safe_rider", "severity_claim_ratio", "rider_experience_index"
            ] + part_cols
        else:
            raise ValueError(f"Unknown dataset_type: {dataset_type}")

        return groups

    @classmethod
    def build_preprocessing_pipeline(cls, dataset_type: str, output_pandas: bool = True) -> Pipeline:
        """
        Builds the modular preprocessing pipeline (ColumnTransformer + Encoders + Scalers).

        Args:
            dataset_type: One of 'car_quotation', 'bike_quotation', 'car_claims', 'bike_claims'.
            output_pandas: If True, configures the pipeline to return a Pandas DataFrame.

        Returns:
            Pipeline: Scikit-learn Pipeline object containing the ColumnTransformer.
        """
        logger.info("Building preprocessing pipeline for dataset_type: %s", dataset_type)
        groups = cls.get_feature_groups(dataset_type)

        # Build individual transformers
        robust_pipeline = Pipeline([
            ("log1p", FunctionTransformer(np.log1p, validate=False)),
            ("robust_scaler", RobustScaler())
        ])

        transformers = []

        if groups["robust_features"]:
            transformers.append(("robust", robust_pipeline, groups["robust_features"]))
        
        if groups["standard_features"]:
            transformers.append(("standard", StandardScaler(), groups["standard_features"]))

        if groups["minmax_features"]:
            transformers.append(("minmax", MinMaxScaler(), groups["minmax_features"]))

        if groups["ohe_features"]:
            transformers.append(("ohe", OneHotEncoder(drop="first", sparse_output=False, handle_unknown="ignore"), groups["ohe_features"]))

        if groups["target_features"]:
            transformers.append(("target", TargetEncoder(), groups["target_features"]))

        if groups["passthru_features"]:
            transformers.append(("passthru", "passthrough", groups["passthru_features"]))

        # Assemble ColumnTransformer
        preprocessor = ColumnTransformer(
            transformers=transformers,
            remainder="drop"
        )

        # Assemble final pipeline wrapper
        pipeline = Pipeline(steps=[
            ("col_transformer", preprocessor)
        ])

        if output_pandas:
            try:
                pipeline.set_output(transform="pandas")
                logger.info("Configured pipeline output to return Pandas DataFrame.")
            except Exception as e:
                logger.warning("Could not set_output to pandas. Defaulting to numpy arrays. Error: %s", e)

        return pipeline
