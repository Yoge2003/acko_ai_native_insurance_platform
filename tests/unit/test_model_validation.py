"""
Unit tests for the ACKO ML Model Validation, Residual diagnostics, and reporting.
"""

import os
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier

from src.ml.validation import (
    CrossValidator,
    ErrorAnalyzer,
    RegressionValidator,
    ClassificationValidator,
    ValidationReportGenerator,
)


def make_mock_data(size=100) -> tuple:
    np.random.seed(42)
    # Features
    X = pd.DataFrame({
        "num__age": np.random.uniform(18, 70, size),
        "num__experience": np.random.uniform(0, 50, size),
        "cat__city": np.random.choice([0, 1], size),
    })
    # Target
    y_reg = pd.Series(1000.0 + X["num__age"] * 50 + np.random.normal(0, 100, size), name="annual_premium")
    y_clf = pd.Series(np.random.binomial(1, 0.7, size), name="claim_approved")
    return X, y_reg, y_clf


def test_cross_validator_regression() -> None:
    """Verifies standard 5-Fold cross validation execution on regression."""
    X, y_reg, _ = make_mock_data(100)
    model = RandomForestRegressor(n_estimators=5, random_state=42)
    
    cv_res = CrossValidator.run_regression_cv(model, X, y_reg, n_splits=3)
    assert "r2_mean" in cv_res
    assert "r2_std" in cv_res
    assert "rmse_mean" in cv_res
    assert "mae_mean" in cv_res
    assert isinstance(cv_res["raw"]["r2"], list)
    assert len(cv_res["raw"]["r2"]) == 3


def test_cross_validator_classification() -> None:
    """Verifies stratified 5-Fold cross validation execution on classifiers."""
    X, _, y_clf = make_mock_data(100)
    model = RandomForestClassifier(n_estimators=5, random_state=42)
    
    cv_res = CrossValidator.run_classification_cv(model, X, y_clf, n_splits=3)
    assert "accuracy_mean" in cv_res
    assert "f1_score_mean" in cv_res
    assert "roc_auc_mean" in cv_res
    assert "mcc_mean" in cv_res
    assert len(cv_res["raw"]) == 3


def test_residual_analysis_plots(tmp_path) -> None:
    """Verifies that residual analyzer computes stats and creates plots."""
    X, y_reg, _ = make_mock_data(100)
    model = RandomForestRegressor(n_estimators=5, random_state=42)
    model.fit(X, y_reg)
    preds = model.predict(X)
    
    output_dir = str(tmp_path / "plots")
    res_res = ErrorAnalyzer.analyze_regression_residuals(y_reg, preds, output_dir, "Mock_Model")
    
    assert "mean" in res_res
    assert "std" in res_res
    assert os.path.exists(res_res["paths"]["histogram"])
    assert os.path.exists(res_res["paths"]["qq_plot"])
    assert os.path.exists(res_res["paths"]["predicted_vs_actual"])
    assert os.path.exists(res_res["paths"]["residual_vs_prediction"])


def test_misclassification_analysis() -> None:
    """Verifies that misclassification analyzer profiles confidence levels and top features."""
    X, _, y_clf = make_mock_data(100)
    model = RandomForestClassifier(n_estimators=5, random_state=42)
    model.fit(X, y_clf)
    preds = model.predict(X)
    probs = model.predict_proba(X)[:, 1]
    
    misclass = ErrorAnalyzer.analyze_classification_errors(X, y_clf, preds, probs)
    assert "num_false_positives" in misclass
    assert "num_false_negatives" in misclass
    assert "mean_confidence_fp" in misclass
    assert "mean_confidence_fn" in misclass
    assert "top_reasons" in misclass


def test_validation_report_generation(tmp_path) -> None:
    """Verifies report generation and score calculation."""
    # Build complete mock reports dicts
    mock_reg_res = {
        "cv_results": {"r2_mean": 0.88, "r2_std": 0.015, "r2_var": 0.000225, "rmse_mean": 320.0, "mae_mean": 240.0},
        "residual_results": {"mean": 12.0, "std": 310.0},
        "generalization_gap": 0.04
    }
    mock_clf_res = {
        "cv_results": {
            "accuracy_mean": 0.89, "accuracy_std": 0.01,
            "precision_mean": 0.91, "precision_std": 0.01,
            "recall_mean": 0.93, "recall_std": 0.01,
            "f1_score_mean": 0.92, "f1_score_std": 0.01,
            "roc_auc_mean": 0.94, "roc_auc_std": 0.008,
            "balanced_accuracy_mean": 0.87, "balanced_accuracy_std": 0.01,
            "mcc_mean": 0.68, "mcc_std": 0.015
        },
        "misclassification_results": {
            "num_false_positives": 5, "mean_confidence_fp": 0.54,
            "num_false_negatives": 6, "mean_confidence_fn": 0.46,
            "num_correct": 89, "mean_confidence_correct": 0.82,
            "top_reasons": [{"feature": "num__age", "mean_correct": 42.5, "mean_incorrect": 32.1, "std_difference": 1.25}]
        }
    }
    
    report_file = os.path.join(tmp_path, "model_validation_report.md")
    ValidationReportGenerator.generate_report(mock_reg_res, mock_reg_res, mock_clf_res, mock_clf_res, report_file)
    assert os.path.exists(report_file)
    
    with open(report_file, "r") as f:
        content = f.read()
    assert "Model Validation & Error Analysis Report" in content
    assert "Car Premium regression Model" in content
    assert "100/100" in content  # Target score: 100/100 based on standard calculations
