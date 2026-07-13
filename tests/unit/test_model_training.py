"""
Unit tests for the ACKO ML Quotation Model Training, Evaluation, and Selection Pipeline.
"""

import sys
import traceback
from pathlib import Path
import numpy as np
import pandas as pd

# Add project root to sys.path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.ml.models import (
    ModelFactory,
    ModelEvaluator,
    BaseTrainer,
    CarQuotationTrainer,
    BikeQuotationTrainer,
)


def make_mock_data_package(size=50) -> dict:
    """Generates mock prepared dataset packages for testing."""
    np.random.seed(42)
    # Features
    X = pd.DataFrame({
        "num__age": np.random.uniform(18, 70, size),
        "num__idv": np.random.uniform(20000, 1000000, size),
        "cat__make_Honda": np.random.choice([0, 1], size),
        "cat__make_Tata": np.random.choice([0, 1], size),
        "bool__is_electric": np.random.choice([0, 1], size),
    })
    # Target (linear combination plus some noise)
    y = 5000 + X["num__age"] * 80 + X["num__idv"] * 0.02 + np.random.normal(0, 500, size)
    y = pd.Series(y, name="annual_premium")

    return {
        "X_train": X,
        "X_val": X.copy(),
        "X_test": X.copy(),
        "y_train": y,
        "y_val": y.copy(),
        "y_test": y.copy(),
        "feature_names": list(X.columns),
        "raw_metadata": {"dataset_type": "car_quotation", "target_column": "annual_premium"}
    }


def test_model_factory_returns_dict() -> None:
    """Verifies that ModelFactory instantiates correct number of models and keys."""
    models = ModelFactory.get_regression_models()
    assert isinstance(models, dict)
    assert len(models) == 7
    expected_keys = [
        "linear_regression",
        "decision_tree",
        "random_forest",
        "extra_trees",
        "gradient_boosting",
        "xgboost",
        "lightgbm",
    ]
    for key in expected_keys:
        assert key in models


def test_model_evaluator_metrics() -> None:
    """Verifies that ModelEvaluator correctly calculates MAE, RMSE, R2, and MAPE."""
    y_true = np.array([100.0, 200.0, 300.0])
    y_pred = np.array([110.0, 190.0, 310.0])

    metrics = ModelEvaluator.evaluate_regression(y_true, y_pred)
    assert "R2" in metrics
    assert "RMSE" in metrics
    assert "MAE" in metrics
    assert "MAPE" in metrics

    # MAE should be (10 + 10 + 10) / 3 = 10
    assert abs(metrics["MAE"] - 10.0) < 1e-5
    
    # Overfitting checker
    is_overfit, gap = ModelEvaluator.check_overfitting(0.95, 0.90, threshold=0.1)
    assert is_overfit is False
    assert abs(gap - 0.05) < 1e-5

    is_overfit_true, gap_true = ModelEvaluator.check_overfitting(0.95, 0.70, threshold=0.1)
    assert is_overfit_true is True


def test_car_quotation_trainer_pipeline() -> None:
    """Verifies that CarQuotationTrainer fits all models, creates comparative table and selects best."""
    pkg = make_mock_data_package(60)
    trainer = CarQuotationTrainer(pkg)

    # 1. Train and evaluate
    comparison_df = trainer.train_and_evaluate_all(sample_size=None)
    assert isinstance(comparison_df, pd.DataFrame)
    assert len(comparison_df) == 7
    assert "val_R2" in comparison_df.columns
    assert "train_time_sec" in comparison_df.columns

    # 2. Select best model
    name, model, reason = trainer.select_best_model(tolerance=0.02)
    assert name in trainer.trained_models
    assert trainer.best_model_name == name
    assert trainer.best_model is not None
    assert isinstance(reason, str) and len(reason) > 0

    # 3. Get feature importances
    imp_df = trainer.get_feature_importances()
    assert isinstance(imp_df, pd.DataFrame)
    assert len(imp_df) == len(pkg["feature_names"])
    assert "feature" in imp_df.columns
    assert "importance" in imp_df.columns
    assert imp_df.loc[0, "importance"] >= imp_df.loc[1, "importance"]


def test_bike_quotation_trainer_pipeline() -> None:
    """Verifies that BikeQuotationTrainer executes correctly."""
    pkg = make_mock_data_package(50)
    trainer = BikeQuotationTrainer(pkg)
    
    comparison_df = trainer.train_and_evaluate_all(sample_size=30)
    assert len(comparison_df) == 7
    
    name, _, _ = trainer.select_best_model()
    assert name == "random_forest"


def test_production_model_training_mode() -> None:
    """Verifies that trainers can run fits for Random Forest alone, without full candidate iteration."""
    pkg = make_mock_data_package(40)
    trainer = CarQuotationTrainer(pkg)
    
    # Run production mode
    model = trainer.train_production_model(use_full_data=False)
    assert model.__class__.__name__ == "RandomForestRegressor"
    assert trainer.best_model_name == "random_forest"
    assert trainer.best_model is model
    
    # Feature importances must still extract correctly
    imp_df = trainer.get_feature_importances()
    assert len(imp_df) == len(pkg["feature_names"])



if __name__ == "__main__":
    print("=" * 60)
    print("ACKO Insurance Models - Running Quotation Model Training Unit Tests")
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
