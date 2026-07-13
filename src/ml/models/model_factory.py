"""
Model Factory.
Instantiates candidate regression and classification models for quotation premium prediction and claims approval classification.
"""

import logging
from typing import Dict, Any
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.tree import DecisionTreeRegressor, DecisionTreeClassifier
from sklearn.ensemble import (
    RandomForestRegressor,
    ExtraTreesRegressor,
    GradientBoostingRegressor,
    RandomForestClassifier,
    ExtraTreesClassifier,
    GradientBoostingClassifier,
)
import xgboost as xgb
import lightgbm as lgb

# Set up logger
logger = logging.getLogger(__name__)


class ModelFactory:
    """
    Factory for producing candidate estimators.
    Generates regression and classification estimators using sensible default parameter boundaries for fast fitting.
    """

    @staticmethod
    def get_regression_models() -> Dict[str, Any]:
        """
        Retrieves the suite of candidate regression models.

        Models:
            1. Linear Regression
            2. Decision Tree Regressor (max_depth=8)
            3. Random Forest Regressor (n_estimators=30, max_depth=8, n_jobs=-1)
            4. Extra Trees Regressor (n_estimators=30, max_depth=8, n_jobs=-1)
            5. Gradient Boosting Regressor (n_estimators=30, max_depth=4)
            6. XGBoost Regressor (n_estimators=30, max_depth=5, n_jobs=-1)
            7. LightGBM Regressor (n_estimators=30, max_depth=5, n_jobs=-1, verbose=-1)

        Returns:
            Dict[str, Any]: Mapping of model names to instantiated regressors.
        """
        logger.info("Initializing candidate models collection from ModelFactory.")
        
        models = {
            "linear_regression": LinearRegression(),
            
            "decision_tree": DecisionTreeRegressor(
                max_depth=8, 
                random_state=42
            ),
            
            "random_forest": RandomForestRegressor(
                n_estimators=30, 
                max_depth=8, 
                random_state=42, 
                n_jobs=-1
            ),
            
            "extra_trees": ExtraTreesRegressor(
                n_estimators=30, 
                max_depth=8, 
                random_state=42, 
                n_jobs=-1
            ),
            
            "gradient_boosting": GradientBoostingRegressor(
                n_estimators=30, 
                max_depth=4, 
                random_state=42
            ),
            
            "xgboost": xgb.XGBRegressor(
                n_estimators=30, 
                max_depth=5, 
                random_state=42, 
                n_jobs=-1
            ),
            
            "lightgbm": lgb.LGBMRegressor(
                n_estimators=30, 
                max_depth=5, 
                random_state=42, 
                n_jobs=-1, 
                verbosity=-1
            )
        }
        
        logger.info("Created 7 candidate regression models successfully.")
        return models

    @staticmethod
    def get_classification_models() -> Dict[str, Any]:
        """
        Retrieves the suite of candidate classification models.

        Models:
            1. LogisticRegression (class_weight='balanced')
            2. DecisionTreeClassifier (max_depth=8, class_weight='balanced')
            3. RandomForestClassifier (n_estimators=30, max_depth=8, n_jobs=-1, class_weight='balanced')
            4. ExtraTreesClassifier (n_estimators=30, max_depth=8, n_jobs=-1, class_weight='balanced')
            5. GradientBoostingClassifier (n_estimators=30, max_depth=4)
            6. XGBoostClassifier (n_estimators=30, max_depth=5, n_jobs=-1)
            7. LightGBMClassifier (n_estimators=30, max_depth=5, n_jobs=-1, class_weight='balanced', verbosity=-1)

        Returns:
            Dict[str, Any]: Mapping of model names to instantiated classifiers.
        """
        logger.info("Initializing candidate classification models collection from ModelFactory.")
        
        models = {
            "logistic_regression": LogisticRegression(
                random_state=42,
                max_iter=1000,
                class_weight="balanced"
            ),
            
            "decision_tree": DecisionTreeClassifier(
                max_depth=8,
                random_state=42,
                class_weight="balanced"
            ),
            
            "random_forest": RandomForestClassifier(
                n_estimators=30,
                max_depth=8,
                random_state=42,
                n_jobs=-1,
                class_weight="balanced"
            ),
            
            "extra_trees": ExtraTreesClassifier(
                n_estimators=30,
                max_depth=8,
                random_state=42,
                n_jobs=-1,
                class_weight="balanced"
            ),
            
            "gradient_boosting": GradientBoostingClassifier(
                n_estimators=30,
                max_depth=4,
                random_state=42
            ),
            
            "xgboost": xgb.XGBClassifier(
                n_estimators=30,
                max_depth=5,
                random_state=42,
                n_jobs=-1
            ),
            
            "lightgbm": lgb.LGBMClassifier(
                n_estimators=30,
                max_depth=5,
                random_state=42,
                n_jobs=-1,
                class_weight="balanced",
                verbosity=-1
            )
        }
        
        logger.info("Created 7 candidate classification models successfully.")
        return models
