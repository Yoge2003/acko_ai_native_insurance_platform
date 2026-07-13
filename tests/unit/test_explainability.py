"""
Unit tests for the ACKO ML Explainable AI (XAI) modules.
Verifies model loading, feature ordering, SHAP generation, plotting, reports, and narratives.
"""

import os
import shutil
import tempfile
from typing import Any
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier

from src.ml.explainability.quotation_explainer import QuotationExplainer
from src.ml.explainability.claims_explainer import ClaimsExplainer
from src.ml.explainability.shap_explainer import ShapExplainerWrapper
from src.ml.explainability.explanation_report import ExplanationReportGenerator


# Subclass builders to inject mockup components for fast standalone testing
class MockQuotationExplainer(QuotationExplainer):
    """Mock QuotationExplainer utilizing mocked models and splits."""

    def __init__(self, dataset_type: str, model: Any, X_train: pd.DataFrame, X_val: pd.DataFrame, feature_names: list):
        self.dataset_type = dataset_type
        self.model_path = None
        self.model = model
        self.feature_names = feature_names
        self.data_package = {
            "X_train": X_train,
            "X_val": X_val,
            "X_test": X_val,
            "y_train": pd.Series([1000.0] * len(X_train)),
            "feature_names": feature_names
        }


class MockClaimsExplainer(ClaimsExplainer):
    """Mock ClaimsExplainer utilizing mocked models and splits."""

    def __init__(self, dataset_type: str, model: Any, X_train: pd.DataFrame, X_val: pd.DataFrame, feature_names: list):
        self.dataset_type = dataset_type
        self.model_path = None
        self.model = model
        self.feature_names = feature_names
        self.data_package = {
            "X_train": X_train,
            "X_val": X_val,
            "X_test": X_val,
            "y_train": pd.Series([1.0] * len(X_train)),
            "feature_names": feature_names
        }


def make_test_datasets() -> tuple:
    """Helper to compile mockup data frames and random search matrices."""
    np.random.seed(42)
    feature_names = ["num__idv", "num__engine_cc", "num__ncb_percent", "bool__zero_dep_addon"]
    
    # Train data
    X_train = pd.DataFrame({
        "num__idv": np.random.uniform(100000, 800000, 50),
        "num__engine_cc": np.random.choice([1000, 1500, 2000], 50),
        "num__ncb_percent": np.random.choice([0, 20, 50], 50),
        "bool__zero_dep_addon": np.random.choice([0, 1], 50)
    })
    
    # Val data
    X_val = pd.DataFrame({
        "num__idv": np.random.uniform(100000, 800000, 10),
        "num__engine_cc": np.random.choice([1000, 1500, 2000], 10),
        "num__ncb_percent": np.random.choice([0, 20, 50], 10),
        "bool__zero_dep_addon": np.random.choice([0, 1], 10)
    })

    # Fit target labels
    y_reg = 1000.0 + X_train["num__idv"] * 0.05 + np.random.normal(0, 50, 50)
    y_clf = np.random.binomial(1, 0.6, 50)

    # Fit models
    reg_model = RandomForestRegressor(n_estimators=5, random_state=42)
    reg_model.fit(X_train, y_reg)

    clf_model = RandomForestClassifier(n_estimators=5, random_state=42)
    clf_model.fit(X_train, y_clf)

    return X_train, X_val, feature_names, reg_model, clf_model


def test_explainer_caching() -> None:
    """Verifies that ShapExplainerWrapper correctly caches TreeExplainer instances."""
    X_train, _, _, reg_model, _ = make_test_datasets()
    
    # Clear cache entries
    ShapExplainerWrapper._explainer_cache.clear()
    
    exp1 = ShapExplainerWrapper.get_explainer("test_key", reg_model)
    exp2 = ShapExplainerWrapper.get_explainer("test_key", reg_model)
    
    assert exp1 is exp2
    assert "test_key" in ShapExplainerWrapper._explainer_cache


def test_quotation_explainer_local() -> None:
    """Verifies QuotationExplainer computes local SHAP values and makes readable text."""
    X_train, X_val, feature_names, reg_model, _ = make_test_datasets()
    explainer = MockQuotationExplainer("car_quotation", reg_model, X_train, X_val, feature_names)
    
    # Compute local prediction
    res = explainer.explain_prediction(X_val.head(1))
    
    assert "expected_value" in res
    assert "prediction_value" in res
    assert "top_positive_contributors" in res
    assert "explanation_text" in res
    assert isinstance(res["explanation_text"], str)
    assert len(res["top_positive_contributors"]) > 0


def test_claims_explainer_local() -> None:
    """Verifies ClaimsExplainer computes local probability SHAP values and makes readable text."""
    X_train, X_val, feature_names, _, clf_model = make_test_datasets()
    explainer = MockClaimsExplainer("car_claims", clf_model, X_train, X_val, feature_names)
    
    # Compute local prediction
    res = explainer.explain_prediction(X_val.head(1))
    
    assert "expected_value" in res
    assert "prediction_value" in res
    assert "top_positive_contributors" in res
    assert "explanation_text" in res
    assert isinstance(res["explanation_text"], str)
    assert len(res["top_positive_contributors"]) > 0


def test_explain_global() -> None:
    """Verifies that global explanation profiles generate comparisons and rank outputs."""
    X_train, X_val, feature_names, reg_model, _ = make_test_datasets()
    explainer = MockQuotationExplainer("car_quotation", reg_model, X_train, X_val, feature_names)
    
    global_res = explainer.explain_global(max_samples=10)
    
    assert "global_rankings" in global_res
    ranks = global_res["global_rankings"]
    assert len(ranks) == len(feature_names)
    assert "shap_importance" in ranks[0]
    assert "rf_importance" in ranks[0]
    # Should be sorted
    assert ranks[0]["shap_importance"] >= ranks[-1]["shap_importance"]


def test_save_visualizations() -> None:
    """Verifies that plotting routines write the 6 SHAP plot variants to disk."""
    X_train, X_val, feature_names, reg_model, _ = make_test_datasets()
    explainer = MockQuotationExplainer("car_quotation", reg_model, X_train, X_val, feature_names)
    
    temp_dir = tempfile.mkdtemp()
    try:
        saved_paths = explainer.save_visualizations(X_val, temp_dir, "Test Model")
        
        # Verify plots were generated
        assert len(saved_paths) > 0
        for p in saved_paths:
            assert os.path.exists(p)
    finally:
        shutil.rmtree(temp_dir)


def test_generate_report() -> None:
    """Verifies that individual explainers can write model-specific reports."""
    X_train, X_val, feature_names, reg_model, _ = make_test_datasets()
    explainer = MockQuotationExplainer("car_quotation", reg_model, X_train, X_val, feature_names)
    
    temp_dir = tempfile.mkdtemp()
    try:
        report_path = os.path.join(temp_dir, "model_report.md")
        explainer.generate_report(report_path)
        assert os.path.exists(report_path)
        with open(report_path, "r", encoding="utf-8") as f:
            content = f.read()
        assert "Model-Specific SHAP Explainability Report" in content
    finally:
        shutil.rmtree(temp_dir)


def test_unified_report() -> None:
    """Verifies compilation of the final aggregated explainability validation report."""
    X_train, X_val, feature_names, reg_model, clf_model = make_test_datasets()
    
    q_exp = MockQuotationExplainer("car_quotation", reg_model, X_train, X_val, feature_names)
    c_exp = MockClaimsExplainer("car_claims", clf_model, X_train, X_val, feature_names)
    
    q_global = q_exp.explain_global(max_samples=10)["global_rankings"]
    q_local = q_exp.explain_prediction(X_val)
    
    c_global = c_exp.explain_global(max_samples=10)["global_rankings"]
    c_local = c_exp.explain_prediction(X_val)

    temp_dir = tempfile.mkdtemp()
    try:
        report_path = os.path.join(temp_dir, "shap_report.md")
        ExplanationReportGenerator.generate_report(
            car_prem_global=q_global,
            car_prem_local=q_local,
            bike_prem_global=q_global,
            bike_prem_local=q_local,
            car_claims_global=c_global,
            car_claims_local=c_local,
            bike_claims_global=c_global,
            bike_claims_local=c_local,
            output_path=report_path
        )
        assert os.path.exists(report_path)
        with open(report_path, "r", encoding="utf-8") as f:
            content = f.read()
        assert "Explainable AI (XAI) & SHAP Validation Report" in content
        assert "Car Premium Feature Rankings" in content
    finally:
        shutil.rmtree(temp_dir)
