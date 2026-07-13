"""
Unit tests for the ACKO ML Preprocessing and Feature Engineering Pipelines.
Validates DataLoader, Preprocessors, Feature Engineers, PipelineFactory, and Pipeline saving/loading.
"""

import os
import traceback
import sys
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline

try:
    import pytest
except ImportError:
    # Minimal mock of pytest to run without external dependencies
    class pytest:
        class raises:
            def __init__(self, expected_exception):
                self.expected_exception = expected_exception
            def __enter__(self):
                return self
            def __exit__(self, exc_type, exc_val, exc_tb):
                if exc_type is None:
                    raise AssertionError(f"Did not raise {self.expected_exception.__name__}")
                if not issubclass(exc_type, self.expected_exception):
                    raise AssertionError(f"Expected {self.expected_exception.__name__}, got {exc_type.__name__}")
                return True
        @staticmethod
        def skip(reason):
            raise RuntimeWarning(f"Skipped: {reason}")


from src.ml.preprocessing import (
    DataLoader,
    CarQuotationPreprocessor,
    BikeQuotationPreprocessor,
    CarClaimsPreprocessor,
    BikeClaimsPreprocessor,
    PipelineFactory,
    save_pipeline,
    load_pipeline,
)

from src.ml.feature_engineering import (
    CarQuotationFeatureEngineer,
    BikeQuotationFeatureEngineer,
    CarClaimsFeatureEngineer,
    BikeClaimsFeatureEngineer,
    run_feature_pipeline,
)


# Helper to generate Mock Citation data having the exact schema
def make_mock_car_quotation_df(num_rows: int = 15) -> pd.DataFrame:
    def rep(lst):
        return (lst * (num_rows // len(lst) + 1))[:num_rows]
    data = {
        "record_id": [f"rec_{i}" for i in range(num_rows)],
        "customer_age": rep([25, 35, 45, 55, 65]),
        "city": rep(["Mumbai", "Delhi", "Bengaluru", "Pune", "Chennai"]),
        "state": rep(["MH", "DL", "KA", "MH", "TN"]),
        "city_tier": rep([1, 1, 2, 2, 1]),
        "city_risk_score": rep([1.2, 1.4, 0.9, 1.1, 1.0]),
        "vehicle_make": rep(["Honda", "Maruti", "Hyundai", "Tata", "Mahindra"]),
        "vehicle_model": rep(["City", "Swift", "i20", "Nexon", "Thar"]),
        "variant": rep(["VXI", "LXI", "Asta", "XM", "LX"]),
        "segment": rep(["Sedan", "Hatchback", "Premium Hatch", "SUV", "SUV"]),
        "fuel_type": rep(["Petrol", "Petrol", "EV", "Diesel", "Diesel"]),
        "colour": rep(["Red", "Blue", "White", "Silver", "Black"]),
        "manufacturing_year": rep([2021, 2022, 2023, 2020, 2019]),
        "vehicle_age_years": rep([2, 1, 0, 3, 4]),
        "engine_cc": rep([1498, 1197, 0, 1497, 2184]), # EV is 0
        "idv": rep([800000.0, 450000.0, 1200000.0, 600000.0, 1500000.0]),
        "ncb_percent": rep([20, 0, 50, 35, 45]),
        "claim_history_count": rep([1, 0, 0, 2, 1]),
        "policy_type": rep(["Comprehensive", "Third Party", "Comprehensive", "Own Damage", "Comprehensive"]),
        "previous_insurer": rep(["ICICI", "New India", None, "HDFC Ergo", None]), # Contains Nulls
        "num_addons": rep([2, 0, 4, 1, 3]),
        "addons_list": rep([
            "Roadside Assistance, Zero Depreciation",
            None,
            "Roadside Assistance, Zero Depreciation, Key Replacement, Consumables Cover",
            "Roadside Assistance",
            "Zero Depreciation, Personal Accident Cover, Tyre Protection"
        ]),
        "od_premium_before_ncb": rep([12000.0, 0.0, 18000.0, 8000.0, 15000.0]),
        "ncb_discount_amount": rep([2400.0, 0.0, 9000.0, 2800.0, 6750.0]),
        "tp_premium": rep([3227.0, 2072.0, 0.0, 3227.0, 7890.0]),
        "addon_premium": rep([2500.0, 0.0, 6000.0, 1000.0, 4500.0]),
        "gst_amount": rep([2754.0, 373.0, 2700.0, 1517.0, 3105.0]),
        "annual_premium": [15281.0 + float(i) * 1.5 for i in range(num_rows)]
    }
    return pd.DataFrame(data)


def make_mock_bike_quotation_df(num_rows: int = 15) -> pd.DataFrame:
    def rep(lst):
        return (lst * (num_rows // len(lst) + 1))[:num_rows]
    data = {
        "record_id": [f"rec_{i}" for i in range(num_rows)],
        "customer_age": rep([22, 28, 35, 42, 50]),
        "city": rep(["Mumbai", "Delhi", "Bengaluru", "Pune", "Chennai"]),
        "state": rep(["MH", "DL", "KA", "MH", "TN"]),
        "city_tier": rep([1, 1, 2, 2, 1]),
        "city_risk_score": rep([1.1, 1.3, 0.85, 1.0, 0.95]),
        "vehicle_make": rep(["Hero", "Honda", "TVS", "Bajaj", "Ather"]),
        "vehicle_model": rep(["Splendor", "Activa", "Jupiter", "Pulsar", "455X"]),
        "variant": rep(["Standard", "DLX", "ZX", "Neon", "Pro"]),
        "segment": rep(["Commuter", "Scooter", "Scooter", "Sports", "Electric Scooter"]),
        "fuel_type": rep(["Petrol", "Petrol", "Petrol", "Petrol", "Electric"]),
        "colour": rep(["Black", "Grey", "Blue", "Red", "White"]),
        "manufacturing_year": rep([2021, 2022, 2023, 2020, 2024]),
        "vehicle_age_years": rep([2, 1, 0, 3, 0]),
        "engine_cc": rep([97, 109, 109, 149, 0]),
        "idv": rep([55000.0, 60000.0, 65000.0, 80000.0, 120000.0]),
        "ncb_percent": rep([20, 0, 50, 35, 0]),
        "claim_history_count": rep([1, 0, 0, 2, 0]),
        "policy_type": rep(["Comprehensive", "Third Party", "Comprehensive", "Own Damage", "Comprehensive"]),
        "usage_type": rep(["Personal", "Delivery", "Personal", "Commercial", "Delivery"]),
        "num_addons": rep([1, 0, 2, 0, 3]),
        "addons_list": rep([
            "roadside_assistance",
            None,
            "roadside_assistance, zero_depreciation",
            "None",
            "roadside_assistance, zero_depreciation, engine_protection"
        ]),
        "od_premium_before_ncb": rep([1500.0, 0.0, 2200.0, 700.0, 3000.0]),
        "ncb_discount_amount": rep([300.0, 0.0, 1100.0, 245.0, 0.0]),
        "tp_premium": rep([714.0, 714.0, 0.0, 714.0, 0.0]),
        "addon_premium": rep([250.0, 0.0, 800.0, 0.0, 1500.0]),
        "gst_amount": rep([389.0, 128.0, 342.0, 210.0, 810.0]),
        "annual_premium": [2153.0 + float(i) * 1.5 for i in range(num_rows)]
    }
    return pd.DataFrame(data)


def make_mock_car_claims_df(num_rows: int = 15) -> pd.DataFrame:
    def rep(lst):
        return (lst * (num_rows // len(lst) + 1))[:num_rows]
    data = {
        "record_id": [f"rec_{i}" for i in range(num_rows)],
        "customer_age": rep([30, 40, 25, 55, 48]),
        "city": rep(["Mumbai", "Delhi", "Bengaluru", "Pune", "Chennai"]),
        "state": rep(["MH", "DL", "KA", "MH", "TN"]),
        "city_tier": rep([1, 1, 2, 2, 1]),
        "city_risk_score": rep([1.1, 1.25, 0.9, 1.05, 1.0]),
        "vehicle_make": rep(["Honda", "Maruti", "Hyundai", "Tata", "Nissan"]),
        "vehicle_model": rep(["City", "Swift", "i20", "Nexon", "Magnite"]),
        "segment": rep(["Sedan", "Hatchback", "Premium Hatch", "SUV", "SUV"]),
        "engine_cc": rep([1498, 1197, 0, 1497, 999]),
        "manufacturing_year": rep([2021, 2022, 2023, 2020, 2022]),
        "vehicle_age_years": rep([2, 1, 0, 3, 1]),
        "idv": rep([800000.0, 450000.0, 1200000.0, 650000.0, 700000.0]),
        "policy_type": rep(["Comprehensive", "Third Party", "Comprehensive", "Own Damage", "Comprehensive"]),
        "policy_age_months": rep([14, 5, 2, 35, 11]),
        "annual_premium_paid": rep([15200.0, 3500.0, 18500.0, 9200.0, 12000.0]),
        "previous_claims_count": rep([0, 4, 1, 0, 2]),
        "ncb_at_claim_percent": rep([20, 0, 50, 35, 25]),
        "zero_dep_addon": rep([1, 0, 1, 0, 0]),
        "engine_protection_addon": rep([1, 0, 1, 0, 0]),
        "incident_date": rep(["2021-03-12", "2023-07-20", "2020-03-17", "2022-08-15", "2021-12-05"]),
        "incident_day_of_week": rep(["Friday", "Thursday", "Tuesday", "Monday", "Sunday"]),
        "incident_month": rep([3, 7, 3, 8, 12]),
        "incident_time_of_day": rep(["Night", "Afternoon", "Afternoon", "Night", "Morning"]),
        "incident_type": rep(["Accident", "Flooding", "Accident", "Flooding", "Theft"]),
        "damage_type": rep(["Windshield", "Engine", "Bumper", "Engine", "Body"]),
        "damage_severity_score": rep([0.2, 0.8, 0.1, 0.9, 1.0]),
        "num_parts_affected": rep([1, 3, 1, 4, 0]),
        "affected_parts": rep(["windshield", "engine, radiator, hood", "bumper", "engine, radiator, bumper, windshield", None]),
        "claim_amount": rep([15000.0, 250000.0, 8000.0, 350000.0, 700000.0]),
        "approval_probability": rep([0.95, 0.12, 0.98, 0.05, 0.99]),
        "claim_approved": rep([1, 0, 1, 0, 1])
    }
    return pd.DataFrame(data)


def make_mock_bike_claims_df(num_rows: int = 15) -> pd.DataFrame:
    def rep(lst):
        return (lst * (num_rows // len(lst) + 1))[:num_rows]
    data = {
        "record_id": [f"rec_{i}" for i in range(num_rows)],
        "customer_age": rep([20, 32, 45, 27, 38]),
        "city": rep(["Mumbai", "Delhi", "Bengaluru", "Pune", "Chennai"]),
        "state": rep(["MH", "DL", "KA", "MH", "TN"]),
        "city_tier": rep([1, 1, 2, 2, 1]),
        "city_risk_score": rep([1.15, 1.3, 0.88, 1.0, 1.0]),
        "vehicle_make": rep(["Hero", "Honda", "TVS", "Bajaj", "Ather"]),
        "vehicle_model": rep(["Splendor", "Activa", "Jupiter", "Pulsar", "455X"]),
        "segment": rep(["Commuter", "Scooter", "Scooter", "Sports", "Electric Scooter"]),
        "engine_cc": rep([97, 109, 109, 149, 0]),
        "manufacturing_year": rep([2021, 2022, 2023, 2020, 2024]),
        "vehicle_age_years": rep([2, 1, 0, 3, 0]),
        "idv": rep([55000.0, 60000.0, 65000.0, 80000.0, 120000.0]),
        "policy_type": rep(["Comprehensive", "Third Party", "Comprehensive", "Own Damage", "Comprehensive"]),
        "policy_age_months": rep([14, 5, 2, 35, 4]),
        "annual_premium_paid": rep([2000.0, 800.0, 2200.0, 1200.0, 5000.0]),
        "previous_claims_count": rep([0, 4, 1, 0, 0]),
        "ncb_at_claim_percent": rep([20, 0, 50, 35, 25]),
        "zero_dep_addon": rep([1, 0, 1, 0, 1]),
        "usage_type": rep(["Personal", "Delivery", "Personal", "Commercial", "Delivery"]),
        "rider_experience_years": rep([2.0, 10.0, 25.0, 4.0, 1.0]),
        "helmet_worn": rep([1, 0, 1, 1, 0]),
        "incident_date": rep(["2021-03-12", "2023-07-20", "2020-03-17", "2022-08-15", "2021-12-05"]),
        "incident_day_of_week": rep(["Friday", "Thursday", "Tuesday", "Monday", "Sunday"]),
        "incident_month": rep([3, 7, 3, 8, 12]),
        "incident_time_of_day": rep(["Night", "Afternoon", "Afternoon", "Night", "Morning"]),
        "incident_type": rep(["Accident", "Accident", "Flooding", "Accident", "Theft"]),
        "damage_type": rep(["handlebar", "exhaust", "rear_fender", "chain_sprocket", "tyres"]),
        "damage_severity_score": rep([0.3, 0.4, 0.1, 0.7, 0.9]),
        "num_parts_affected": rep([1, 1, 2, 1, 3]),
        "affected_parts": rep(["handlebar", "exhaust", "rear_fender, seat", "chain_sprocket", "tyres, brakes, frame"]),
        "claim_amount": rep([5000.0, 15000.0, 3000.0, 25000.0, 95000.0]),
        "approval_probability": rep([0.90, 0.45, 0.98, 0.65, 0.92]),
        "claim_approved": rep([1, 0, 1, 1, 1])
    }
    return pd.DataFrame(data)


# ── DataLoader Tests ─────────────────────────────────────────────────────────

def test_data_loader_path() -> None:
    """Verifies that project root is identified and find_file_path handles relative files."""
    root = DataLoader.get_project_root()
    assert root.exists()
    assert (root / "src").is_dir() or (root / "src").exists()

    with pytest.raises(FileNotFoundError):
        DataLoader.find_file_path("non_existent_file_name_12345.csv")


def test_data_loader_load_real_csv_partial() -> None:
    """Performs partial load integration test on actual CSV files to verify DataLoader."""
    try:
        df = DataLoader.load_csv("acko_car_quotation.csv", nrows=3)
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 3
        assert "annual_premium" in df.columns
        assert "record_id" in df.columns
    except FileNotFoundError:
        pytest.skip("Dataset files are not present in workspace yet.")


# ── Car Quotation Preprocessor & Feature Engineer Tests ──────────────────────

def test_car_quotation_pipeline_steps() -> None:
    """Verifies decoupling of preprocessing and feature engineering for Car Quotation."""
    raw_df = make_mock_car_quotation_df()
    
    # 1. Test Preprocessor only
    preprocessor = CarQuotationPreprocessor()
    df_clean = preprocessor.preprocess(raw_df)
    
    # Assert standard cleaning happened
    assert "previous_insurer" in df_clean.columns
    assert "addons_list" in df_clean.columns
    # Check no engineered features exist in preprocessor output
    assert "is_electric" not in df_clean.columns
    assert "addon_density" not in df_clean.columns
    assert "relative_depreciation" not in df_clean.columns
    assert "driver_experience_index" not in df_clean.columns
    assert "ev_high_risk_flag" not in df_clean.columns
    for addon in CarQuotationFeatureEngineer.KNOWN_ADDONS:
        assert f"addon_{addon.lower().replace(' ', '_')}" not in df_clean.columns

    # 2. Test Feature Engineer
    engineer = CarQuotationFeatureEngineer()
    df_feats = engineer.fit_transform(df_clean)

    # Check that features are correctly created
    assert "is_electric" in df_feats.columns
    assert "addon_density" in df_feats.columns
    assert "relative_depreciation" in df_feats.columns
    assert "driver_experience_index" in df_feats.columns
    assert "ev_high_risk_flag" in df_feats.columns
    
    # Row 0: "Roadside Assistance, Zero Depreciation" -> 2 / 4.0
    assert df_feats.loc[0, "addon_density"] == 0.5
    # Row 0 is Petrol Honda engine_cc=1498 -> is_electric == 0
    assert df_feats.loc[0, "is_electric"] == 0
    # Row 2 engine_cc=0 -> is_electric == 1
    assert df_feats.loc[2, "is_electric"] == 1
    # Check binarization
    assert df_feats.loc[0, "addon_roadside_assistance"] == 1
    assert df_feats.loc[0, "addon_zero_depreciation"] == 1
    assert df_feats.loc[0, "addon_key_replacement"] == 0
    # Original text addons list must be dropped
    assert "addons_list" not in df_feats.columns


# ── Bike Quotation Preprocessor & Feature Engineer Tests ──────────────────────

def test_bike_quotation_pipeline_steps() -> None:
    """Verifies decoupling of preprocessing and feature engineering for Bike Quotation."""
    raw_df = make_mock_bike_quotation_df()
    
    # 1. Test Preprocessor
    preprocessor = BikeQuotationPreprocessor()
    df_clean = preprocessor.preprocess(raw_df)
    
    assert "addons_list" in df_clean.columns
    assert "is_electric" not in df_clean.columns
    assert "usage_risk_score" not in df_clean.columns
    assert "experienced_customer_index" not in df_clean.columns
    assert "is_delivery_ev" not in df_clean.columns

    # 2. Test Feature Engineer
    engineer = BikeQuotationFeatureEngineer()
    df_feats = engineer.fit_transform(df_clean)

    assert "is_electric" in df_feats.columns
    assert "addon_density" in df_feats.columns
    assert "relative_depreciation" in df_feats.columns
    assert "usage_risk_score" in df_feats.columns
    assert "experienced_customer_index" in df_feats.columns
    assert "is_delivery_ev" in df_feats.columns
    
    # Row 1 is Delivery + Petrol (1.3 * 1.6=2.08)
    assert abs(df_feats.loc[1, "usage_risk_score"] - 2.08) < 1e-5
    # Row 4 is Electric Ather -> is_electric == 1
    assert df_feats.loc[4, "is_electric"] == 1
    # Row 4 is Delivery + Electric -> is_delivery_ev == 1
    assert df_feats.loc[4, "is_delivery_ev"] == 1


# ── Car Claims Preprocessor & Feature Engineer Tests ─────────────────────────

def test_car_claims_pipeline_steps() -> None:
    """Verifies decoupling of preprocessing and feature engineering for Car Claims."""
    raw_df = make_mock_car_claims_df()
    
    # 1. Test Preprocessor
    preprocessor = CarClaimsPreprocessor()
    df_clean = preprocessor.preprocess(raw_df)
    
    assert "incident_date" in df_clean.columns
    assert "affected_parts" in df_clean.columns
    assert "incident_day" not in df_clean.columns
    assert "affected_parts_count" not in df_clean.columns
    assert "claim_to_idv_ratio" not in df_clean.columns
    assert "early_claim_flag" not in df_clean.columns
    assert "monsoon_flood_match" not in df_clean.columns

    # 2. Test Feature Engineer
    engineer = CarClaimsFeatureEngineer()
    df_feats = engineer.fit_transform(df_clean)

    assert "incident_day" in df_feats.columns
    assert "affected_parts_count" in df_feats.columns
    assert "claim_to_idv_ratio" in df_feats.columns
    assert "early_claim_flag" in df_feats.columns
    assert "severity_index" in df_feats.columns
    assert "monsoon_flood_match" in df_feats.columns
    assert "addon_coverage_match" in df_feats.columns
    assert "part_bumper" in df_feats.columns

    # Row 0: incident_date="2021-03-12" -> incident_day = 12
    assert df_feats.loc[0, "incident_day"] == 12
    # Row 1: Flooding + Month 7 -> monsoon_flood_match = 1
    assert df_feats.loc[1, "monsoon_flood_match"] == 1
    # Row 1: engine, radiator, hood -> parts count = 3
    assert df_feats.loc[1, "affected_parts_count"] == 3
    # Check drop of string columns
    assert "incident_date" not in df_feats.columns
    assert "affected_parts" not in df_feats.columns


# ── Bike Claims Preprocessor & Feature Engineer Tests ─────────────────────────

def test_bike_claims_pipeline_steps() -> None:
    """Verifies decoupling of preprocessing and feature engineering for Bike Claims."""
    raw_df = make_mock_bike_claims_df()
    
    # 1. Test Preprocessor
    preprocessor = BikeClaimsPreprocessor()
    df_clean = preprocessor.preprocess(raw_df)
    
    assert "incident_date" in df_clean.columns
    assert "affected_parts" in df_clean.columns
    assert "non_helmet_injury_flag" not in df_clean.columns
    assert "experienced_safe_rider" not in df_clean.columns
    assert "rider_experience_index" not in df_clean.columns

    # 2. Test Feature Engineer
    engineer = BikeClaimsFeatureEngineer()
    df_feats = engineer.fit_transform(df_clean)

    assert "non_helmet_injury_flag" in df_feats.columns
    assert "novice_rider_flag" in df_feats.columns
    assert "delivery_high_risk_flag" in df_feats.columns
    assert "experienced_safe_rider" in df_feats.columns
    assert "rider_experience_index" in df_feats.columns
    
    # Row 1: helmet_worn=0, incident_type='Accident' -> non_helmet_injury_flag = 1
    assert df_feats.loc[1, "non_helmet_injury_flag"] == 1
    # Row 0: customer_age=20, exp_years=2.0 -> novice_rider_flag = 1, rider_experience_index = 0.1
    assert df_feats.loc[0, "novice_rider_flag"] == 1
    assert abs(df_feats.loc[0, "rider_experience_index"] - 0.1) < 1e-5


# ── PipelineFactory & persistence layer Tests ────────────────────────────────

def test_pipeline_factory_build_and_fit() -> None:
    """Verifies that generated pipelines can fit and transform datasets using the feature pipeline."""
    raw_df = make_mock_car_quotation_df()
    
    # Run the feature pipeline
    processed_df = run_feature_pipeline(raw_df, "car_quotation")
    
    # Separate X and y
    X = processed_df.drop(columns=["annual_premium"])
    y = processed_df["annual_premium"]

    # Build pipeline
    pipeline = PipelineFactory.build_preprocessing_pipeline("car_quotation")
    assert isinstance(pipeline, Pipeline)

    # Fit and transform
    pipeline.fit(X, y)
    X_transformed = pipeline.transform(X)

    # Check output shape and types
    assert isinstance(X_transformed, pd.DataFrame)
    assert len(X_transformed) == len(X)
    assert X_transformed["target__city"].dtype in [np.float64, np.float32]


def test_pipeline_persistence() -> None:
    """Verifies serialization and deserialization of the fitted pipeline."""
    raw_df = make_mock_bike_quotation_df()
    
    # Run the feature pipeline
    processed_df = run_feature_pipeline(raw_df, "bike_quotation")

    X = processed_df.drop(columns=["annual_premium"])
    y = processed_df["annual_premium"]

    pipeline = PipelineFactory.build_preprocessing_pipeline("bike_quotation")
    pipeline.fit(X, y)

    # Save fitted pipeline
    test_filename = "test_bike_quotation_pipeline.joblib"
    saved_path = save_pipeline(pipeline, test_filename)
    assert saved_path.exists()

    # Load back
    loaded_pipe = load_pipeline(test_filename)
    assert isinstance(loaded_pipe, Pipeline)

    # Verify predictions / transformations match exactly
    original_trans = pipeline.transform(X)
    loaded_trans = loaded_pipe.transform(X)
    pd.testing.assert_frame_equal(original_trans, loaded_trans)

    # Cleanup test pipeline
    if saved_path.exists():
        os.remove(saved_path)

    # Fail cases
    with pytest.raises(ValueError):
        save_pipeline("not_a_pipeline_object", "invalid.joblib")

    with pytest.raises(FileNotFoundError):
        load_pipeline("missing_model_file_9999.joblib")


if __name__ == "__main__":
    print("=" * 60)
    print("ACKO Insurance Pipeline - Running Refactored Unit Tests")
    print("=" * 60)
    
    test_functions = [
        val for key, val in globals().items()
        if key.startswith("test_") and callable(val)
    ]
    
    passed_count = 0
    failed_count = 0
    
    for test_func in test_functions:
        func_name = test_func.__name__
        print(f"Running: {func_name} ... ", end="")
        try:
            test_func()
            print("PASSED")
            passed_count += 1
        except Exception as e:
            if "skipped" in type(e).__name__.lower() or "Skipped:" in str(e) or isinstance(e, RuntimeWarning):
                print("SKIPPED")
            else:
                print("FAILED")
                print("-" * 50)
                traceback.print_exc()
                print("-" * 50)
                failed_count += 1
            
    print("=" * 60)
    print(f"Test Execution Completed: {passed_count} Passed, {failed_count} Failed.")
    print("=" * 60)
    sys.exit(0 if failed_count == 0 else 1)
