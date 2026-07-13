"""
Unit tests for the ACKO ML Training dataset preparation and pipeline modules.
Tests builder, splitter, encoder pipelines, orchestration flows, and artifact serialization.
"""

import os
import shutil
import tempfile
import traceback
import sys
from pathlib import Path
from unittest.mock import patch
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer

# Add src to path just in case
sys.path.append(str(Path(__file__).parent.parent.parent))

try:
    import pytest
except ImportError:
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


from src.ml.training import (
    DatasetBuilder,
    DatasetSplitter,
    EncodingPipeline,
    TrainingPipeline,
    ArtifactManager,
)

# Reuse mock structures from test_preprocessing for unit test standalone speed
def get_mock_car_quotation(nrows=100) -> pd.DataFrame:
    def rep(lst):
        return (lst * (nrows // len(lst) + 1))[:nrows]
    data = {
        "record_id": [f"rec_{i}" for i in range(nrows)],
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
        "vehicle_age_years": rep([2.0, 1.0, 0.0, 3.0, 4.0]),
        "engine_cc": rep([1498, 1197, 0, 1497, 2184]),
        "idv": rep([800000.0, 450000.0, 1200000.0, 600000.0, 1500000.0]),
        "ncb_percent": rep([20, 0, 50, 35, 45]),
        "claim_history_count": rep([1, 0, 0, 2, 1]),
        "policy_type": rep(["Comprehensive", "Third Party", "Comprehensive", "Own Damage", "Comprehensive"]),
        "previous_insurer": rep(["ICICI", "New India", None, "HDFC Ergo", None]),
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
        "annual_premium": [15000.0 + float(i) * 10.0 for i in range(nrows)]
    }
    return pd.DataFrame(data)


def get_mock_car_claims(nrows=100) -> pd.DataFrame:
    def rep(lst):
        return (lst * (nrows // len(lst) + 1))[:nrows]
    data = {
        "record_id": [f"rec_{i}" for i in range(nrows)],
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
        "claim_approved": rep([1, 0, 1, 0, 1]) # Categorical labels
    }
    return pd.DataFrame(data)


# ── Test Dataset Builder ─────────────────────────────────────────────────────

@patch("src.ml.training.dataset_builder.DataLoader.load_csv")
def test_dataset_builder_verification(mock_load) -> None:
    """Verifies DatasetBuilder executes pipelines, separates X and y, and does validation checks."""
    mock_df = get_mock_car_quotation(100)
    mock_load.return_value = mock_df

    # Build dataset
    X, y, meta = DatasetBuilder.build_dataset("car_quotation")

    assert isinstance(X, pd.DataFrame)
    assert isinstance(y, pd.Series)
    assert y.name == "annual_premium"
    
    # Target Leakage check
    assert "od_premium_before_ncb" not in X.columns
    assert "annual_premium" not in X.columns
    assert "record_id" not in X.columns
    assert "manufacturing_year" not in X.columns # dropped as identifier representation

    # Metadata check
    assert meta["dataset_type"] == "car_quotation"
    assert meta["target_column"] == "annual_premium"
    assert len(X) == len(mock_df)

    # Verify duplicates error
    mock_df_dupe = mock_df.copy()
    mock_df_dupe["idv_duplicate"] = mock_df_dupe["idv"]
    # Rename columns to introduce duplicate name
    cols = list(mock_df_dupe.columns)
    cols[-1] = "idv" # force duplicate column name
    mock_df_dupe.columns = cols

    mock_load.return_value = mock_df_dupe
    with pytest.raises(ValueError):
        DatasetBuilder.build_dataset("car_quotation")


# ── Test Dataset Splitter ────────────────────────────────────────────────────

def test_dataset_splitter_allocation() -> None:
    """Verifies that we achieve exactly a 70/15/15 split and stratification is correct."""
    X = pd.DataFrame({"feat1": range(100), "feat2": range(100)})
    # Imbalanced classification target
    y_class = pd.Series([1]*30 + [0]*70)

    # 1. Test standard split (regression)
    X_train, X_valid, X_test, y_train, y_valid, y_test = DatasetSplitter.split(
        X, y_class, stratify=False, random_state=42
    )
    assert len(X_train) == 70
    assert len(X_valid) == 15
    assert len(X_test) == 15

    # 2. Test stratified split (classification)
    X_train_s, X_valid_s, X_test_s, y_train_s, y_valid_s, y_test_s = DatasetSplitter.split(
        X, y_class, stratify=True, random_state=42
    )
    
    # Class distribution targets (1s ratio = 30%)
    train_dist = y_train_s.mean()
    valid_dist = y_valid_s.mean()
    test_dist = y_test_s.mean()

    # Allow tiny rounding deviation (+- 0.05) due to discrete splits
    assert abs(train_dist - 0.3) < 0.05
    assert abs(valid_dist - 0.3) < 0.05
    assert abs(test_dist - 0.3) < 0.05


# ── Test Encoding Pipeline ───────────────────────────────────────────────────

def test_encoding_pipeline_execution() -> None:
    """Verifies imputation of missing values, drop parameters of OHE, and pandas output settings."""
    df_train = pd.DataFrame({
        "num_col": [1.0, np.nan, 3.5, 4.0, 5.0],
        "cat_col": ["A", "B", "A", None, "B"],
        "bool_col": [1, 0, 1, 0, 1]
    })
    # Convert object to string/category to trigger inference
    df_train["cat_col"] = df_train["cat_col"].astype("category")

    encoding_pipeline = EncodingPipeline()
    preprocessor = encoding_pipeline.build_pipeline(df_train)

    assert "num" in [t[0] for t in preprocessor.transformers]
    assert "cat" in [t[0] for t in preprocessor.transformers]
    assert "bool" in [t[0] for t in preprocessor.transformers]

    # Fit transformer
    preprocessor.fit(df_train)

    # Check output
    df_transformed = preprocessor.transform(df_train)
    assert isinstance(df_transformed, pd.DataFrame)
    
    # Null imputation checks
    assert df_transformed["num__num_col"].isna().sum() == 0
    # Imputed value for row 1 should be median = 3.75 or 3.5 depending on calculation
    assert df_transformed.loc[1, "num__num_col"] == 3.75 or df_transformed.loc[1, "num__num_col"] == 3.5
    
    # OHE check (should create cat__cat_col_A and cat__cat_col_B)
    assert "cat__cat_col_A" in df_transformed.columns
    assert "cat__cat_col_B" in df_transformed.columns


# ── Test Training Pipeline ────────────────────────────────────────────────────

@patch("src.ml.training.dataset_builder.DataLoader.load_csv")
def test_training_pipeline_orchestration(mock_load) -> None:
    """Verifies end-to-end execution of orchestration class for Quotation & Claims."""
    # 1. Test Car Quotation
    mock_load.return_value = get_mock_car_quotation(100)
    data_pack = TrainingPipeline.run_pipeline("car_quotation")

    assert "X_train" in data_pack
    assert "X_val" in data_pack
    assert "X_test" in data_pack
    assert "y_train" in data_pack
    assert "encoding_pipeline" in data_pack
    assert "feature_names" in data_pack

    # Verify exact schema lengths
    assert len(data_pack["X_train"]) == 70
    assert len(data_pack["X_val"]) == 15
    assert len(data_pack["X_test"]) == 15

    # Check that output is DataFrame and columns align
    assert data_pack["X_train"].columns.tolist() == data_pack["X_val"].columns.tolist()


# ── Test Artifact Manager ─────────────────────────────────────────────────────

@patch("src.ml.training.dataset_builder.DataLoader.load_csv")
def test_artifact_manager_persistence(mock_load) -> None:
    """Verifies that we save/load details, feature name consistency, and folder structures."""
    mock_load.return_value = get_mock_car_claims(100)
    data_pack = TrainingPipeline.run_pipeline("car_claims")

    # Create temp directory
    temp_dir = tempfile.mkdtemp()
    try:
        # Save artifacts
        filepath = ArtifactManager.save_artifacts(
            dataset_type="car_claims",
            transformer=data_pack["encoding_pipeline"].transformer,
            feature_names=data_pack["feature_names"],
            target_name="claim_approved",
            raw_metadata=data_pack["raw_metadata"],
            X_train=data_pack["X_train"],
            y_train=data_pack["y_train"],
            custom_dir=temp_dir
        )
        assert filepath.exists()

        # Load back
        package = ArtifactManager.load_artifacts("car_claims", custom_dir=temp_dir)
        
        assert package["dataset_type"] == "car_claims"
        assert package["target_name"] == "claim_approved"
        assert package["feature_names"] == data_pack["feature_names"]
        assert isinstance(package["transformer"], ColumnTransformer)
        
        # Verify stats compile
        assert "dataset_statistics" in package
        assert package["dataset_statistics"]["num_samples"] == 70
        assert package["dataset_statistics"]["num_features"] == len(data_pack["feature_names"])

    finally:
        shutil.rmtree(temp_dir)


if __name__ == "__main__":
    print("=" * 60)
    print("ACKO Insurance ML Training Preparation - Running Unit Tests")
    print("=" * 60)

    test_funcs = [
        val for key, val in globals().items()
        if key.startswith("test_") and callable(val)
    ]

    passed_count = 0
    failed_count = 0

    for test_func in test_funcs:
        func_name = test_func.__name__
        print(f"Running: {func_name} ... ", end="")
        try:
            test_func()
            print("PASSED")
            passed_count += 1
        except Exception as e:
            print("FAILED")
            print("-" * 50)
            traceback.print_exc()
            print("-" * 50)
            failed_count += 1

    print("=" * 60)
    print(f"Test Execution Completed: {passed_count} Passed, {failed_count} Failed.")
    print("=" * 60)
    sys.exit(0 if failed_count == 0 else 1)
