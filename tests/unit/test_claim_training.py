"""
Unit tests for the ACKO ML Claims Model Training, Evaluation, and Selection Pipeline.
"""

import sys
import numpy as np
import pandas as pd

from src.ml.models import (
    ModelFactory,
    ClassificationEvaluator,
    CarClaimsTrainer,
    BikeClaimsTrainer,
)


def make_mock_classification_data(size=100) -> dict:
    """Generates mock prepared dataset packages for testing classification."""
    np.random.seed(42)
    # Features
    X = pd.DataFrame({
        "num__age": np.random.uniform(18, 70, size),
        "num__driver_experience": np.random.uniform(0, 50, size),
        "cat__city_Mumbai": np.random.choice([0, 1], size),
        "cat__city_Pune": np.random.choice([0, 1], size),
        "bool__is_commercial": np.random.choice([0, 1], size),
    })
    # Target (binary: claim approved or not)
    scores = -2.0 + X["num__age"] * 0.02 + X["num__driver_experience"] * 0.05
    probs = 1 / (1 + np.exp(-scores))
    y = pd.Series(np.random.binomial(1, probs), name="claim_approved")

    return {
        "X_train": X,
        "X_val": X.copy(),
        "X_test": X.copy(),
        "y_train": y,
        "y_val": y.copy(),
        "y_test": y.copy(),
        "feature_names": list(X.columns),
        "raw_metadata": {"dataset_type": "car_claims", "target_column": "claim_approved"}
    }


def test_model_factory_classification() -> None:
    """Verifies that ModelFactory instantiates 7 classification models."""
    models = ModelFactory.get_classification_models()
    assert isinstance(models, dict)
    assert len(models) == 7
    expected = [
        "logistic_regression",
        "decision_tree",
        "random_forest",
        "extra_trees",
        "gradient_boosting",
        "xgboost",
        "lightgbm",
    ]
    for m in expected:
        assert m in models
        
    # Check class weights balanced where supported
    assert models["logistic_regression"].class_weight == "balanced"
    assert models["decision_tree"].class_weight == "balanced"
    assert models["random_forest"].class_weight == "balanced"
    assert models["extra_trees"].class_weight == "balanced"
    assert models["lightgbm"].class_weight == "balanced"
    
    # Check that gradient_boosting and xgboost do NOT have it
    assert not hasattr(models["gradient_boosting"], "class_weight")
    assert not hasattr(models["xgboost"], "class_weight")


def test_classification_evaluator() -> None:
    """Verifies that ClassificationEvaluator returns the 8 correct metrics."""
    y_true = np.array([0, 0, 1, 1, 1, 0, 1])
    y_pred = np.array([0, 0, 1, 0, 1, 1, 1])
    y_prob = np.array([0.1, 0.2, 0.9, 0.4, 0.8, 0.7, 0.95])

    metrics = ClassificationEvaluator.evaluate_classification(y_true, y_pred, y_prob)
    
    for metric in [
        "accuracy",
        "precision",
        "recall",
        "f1_score",
        "roc_auc",
        "balanced_accuracy",
        "mcc",
        "confusion_matrix",
    ]:
        assert metric in metrics

    assert isinstance(metrics["confusion_matrix"], list)
    assert len(metrics["confusion_matrix"]) == 2

    # Verify Trainer Overfitting Checker
    is_overfit, gap = ClassificationEvaluator.check_overfitting(0.95, 0.80, threshold=0.1)
    assert is_overfit is True
    
    is_overfit_false, gap_false = ClassificationEvaluator.check_overfitting(0.95, 0.90, threshold=0.1)
    assert is_overfit_false is False


def test_car_claims_trainer_benchmark_mode() -> None:
    """Verifies CarClaimsTrainer trains in benchmark mode and collects metrics."""
    pkg = make_mock_classification_data(100)
    trainer = CarClaimsTrainer(pkg)
    
    # Run benchmark mode
    comparison_df = trainer.train_and_evaluate_all(sample_size=None)
    assert isinstance(comparison_df, pd.DataFrame)
    assert len(comparison_df) == 7
    assert "val_f1" in comparison_df.columns
    assert "val_roc_auc" in comparison_df.columns
    assert "train_time_sec" in comparison_df.columns
    
    # Selection logic
    name, model, reason = trainer.select_best_model()
    assert name == "random_forest"
    assert trainer.best_model_name == "random_forest"
    assert trainer.best_model is not None
    assert "Selected 'random_forest'" in reason
    
    # Feature importance extraction
    imp_df = trainer.get_feature_importances()
    assert isinstance(imp_df, pd.DataFrame)
    assert len(imp_df) == len(pkg["feature_names"])
    assert "feature" in imp_df.columns
    assert "importance" in imp_df.columns


def test_bike_claims_trainer_benchmark_mode() -> None:
    """Verifies BikeClaimsTrainer executes correctly on benchmark subsets."""
    pkg = make_mock_classification_data(80)
    trainer = BikeClaimsTrainer(pkg)
    
    comparison_df = trainer.train_and_evaluate_all(sample_size=50)
    assert len(comparison_df) == 7
    
    name, _, _ = trainer.select_best_model()
    assert name == "random_forest"


def test_claims_production_mode() -> None:
    """Verifies that claims trainers can run in production mode on full data."""
    pkg = make_mock_classification_data(90)
    trainer = CarClaimsTrainer(pkg)
    
    # Run production mode
    model = trainer.train_production_model(use_full_data=True)
    assert model.__class__.__name__ == "RandomForestClassifier"
    assert trainer.best_model_name == "random_forest"
    assert trainer.best_model is model
    
    # Feature importances must still extract
    imp_df = trainer.get_feature_importances()
    assert len(imp_df) == len(pkg["feature_names"])
