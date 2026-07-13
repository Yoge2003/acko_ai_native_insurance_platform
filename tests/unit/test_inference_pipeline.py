"""
Unit Tests for ML Inference Pipeline.
Verifies loading caches, validation throws, predictors outputs, and SHAP integration accuracy.
"""

import os
import pytest
import pandas as pd

from src.ml.preprocessing.data_loader import DataLoader
from src.ml.inference.quotation_predictor import QuotationPredictor
from src.ml.inference.claims_predictor import ClaimsPredictor
from src.ml.inference.pipeline_validator import PipelineValidator, PipelineValidationError
from src.ml.inference.prediction_pipeline import PredictionPipeline
from src.ml.inference.model_loader import ModelLoader

AUDIT_LOG_FILE = "logs/prediction_audit.csv"


def test_model_loader_caching():
    """
    Verifies that ModelLoader correctly loads and caches estimators and transformers.
    """
    model, transformer, artifacts = ModelLoader.load_components("car_quotation")
    assert model is not None
    assert transformer is not None
    assert "feature_names" in artifacts

    # Run second time, verify it returns identical components instantly
    model_2, transformer_2, _ = ModelLoader.load_components("car_quotation")
    assert model is model_2
    assert transformer is transformer_2


def test_validation_missing_columns():
    """
    Verifies that missing raw columns raise PipelineValidationError.
    """
    predictor = QuotationPredictor("car")
    # Missing required attributes completely
    incomplete_input = {
        "customer_age": 30,
        "city": "Mumbai"
    }
    with pytest.raises(PipelineValidationError) as excinfo:
        predictor.predict(incomplete_input)
    assert "Missing required columns" in str(excinfo.value)


def test_validation_unexpected_columns():
    """
    Verifies that passing columns not present in the expected raw features list raises errors.
    """
    df_raw = DataLoader.load_csv("acko_car_quotation.csv")
    row = df_raw.head(1).to_dict(orient="records")[0]
    
    # Exclude leakages/targets
    leakages = ["od_premium_before_ncb", "ncb_discount_amount", "tp_premium", "addon_premium", "gst_amount", "annual_premium"]
    clean_row = {k: v for k, v in row.items() if k not in leakages}
    
    # Add unexpected entry
    clean_row["hacky_leakage_feature_column"] = 12345
    
    predictor = QuotationPredictor("car")
    with pytest.raises(PipelineValidationError) as excinfo:
        predictor.predict(clean_row)
    assert "Unexpected columns found" in str(excinfo.value)


def test_quotation_predictor_single_and_batch():
    """
    Tests Car Premium predictions and batch results.
    """
    df_raw = DataLoader.load_csv("acko_car_quotation.csv")
    leakages = ["od_premium_before_ncb", "ncb_discount_amount", "tp_premium", "addon_premium", "gst_amount", "annual_premium"]
    
    # Generate 5 records
    records_batch = []
    for _, row in df_raw.head(5).iterrows():
        clean_row = {k: v for k, v in row.to_dict().items() if k not in leakages}
        records_batch.append(clean_row)

    # Test single predict
    predictor = QuotationPredictor("car")
    single_res = predictor.predict(records_batch[0])
    
    assert single_res["prediction_type"] == "premium_quotation"
    assert "predicted_premium" in single_res
    assert isinstance(single_res["predicted_premium"], float)
    assert single_res["currency"] == "INR"
    assert len(single_res["top_positive_features"]) > 0
    assert len(single_res["top_negative_features"]) > 0
    assert "shap_summary" in single_res
    assert "confidence_metadata" in single_res

    # Test batch predict
    batch_res = predictor.predict_batch(records_batch)
    assert isinstance(batch_res, list)
    assert len(batch_res) == 5
    for item in batch_res:
        assert item["prediction_type"] == "premium_quotation"
        assert "predicted_premium" in item


def test_claims_predictor_single_and_batch():
    """
    Tests Car Claims predictions and batch decision results.
    """
    df_raw = DataLoader.load_csv("acko_car_claims.csv")
    leakages = ["approval_probability", "claim_approved"]

    # Generate 3 records
    records_batch = []
    for _, row in df_raw.head(3).iterrows():
        clean_row = {k: v for k, v in row.to_dict().items() if k not in leakages}
        records_batch.append(clean_row)

    # Test single predict
    predictor = ClaimsPredictor("car")
    single_res = predictor.predict(records_batch[0])

    assert single_res["prediction_type"] == "claims_auto_approval"
    assert "claim_prediction" in single_res
    assert isinstance(single_res["claim_prediction"], bool)
    assert "approval_probability" in single_res
    assert isinstance(single_res["approval_probability"], float)
    assert "confidence" in single_res
    assert len(single_res["top_positive_features"]) > 0
    assert len(single_res["top_negative_features"]) > 0
    assert "shap_summary" in single_res
    assert "timestamp" in single_res

    # Test batch predict
    batch_res = predictor.predict_batch(records_batch)
    assert isinstance(batch_res, list)
    assert len(batch_res) == 3
    for item in batch_res:
        assert item["prediction_type"] == "claims_auto_approval"
        assert "claim_prediction" in item


def test_prediction_logging_audit():
    """
    Verifies that MLOps audit metrics are correctly written to the logs CSV file.
    """
    if os.path.exists(AUDIT_LOG_FILE):
        os.remove(AUDIT_LOG_FILE)

    df_raw = DataLoader.load_csv("acko_bike_quotation.csv")
    leakages = ["od_premium_before_ncb", "ncb_discount_amount", "tp_premium", "addon_premium", "gst_amount", "annual_premium"]
    clean_row = {k: v for k, v in df_raw.head(1).to_dict(orient="records")[0].items() if k not in leakages}

    predictor = QuotationPredictor("bike")
    _ = predictor.predict(clean_row)

    # Verify audit CSV file exists and has records
    assert os.path.exists(AUDIT_LOG_FILE)
    df_audit = pd.read_csv(AUDIT_LOG_FILE)
    assert len(df_audit) >= 1
    assert "latency_ms" in df_audit.columns
    assert "input_hash" in df_audit.columns
    assert "prediction_hash" in df_audit.columns
    assert df_audit["dataset_type"].iloc[-1] == "bike_quotation"
