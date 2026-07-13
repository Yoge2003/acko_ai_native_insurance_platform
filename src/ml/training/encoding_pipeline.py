"""
Encoding Pipeline.
Constructs ColumnTransformer to handle numerical imputation and categorical OneHotEncoding.
Avoids scaling and target encoding to prevent data leakage in Random Forest training.
"""

import logging
from typing import List, Tuple
import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.impute import SimpleImputer

# Set up logger
logger = logging.getLogger(__name__)


class EncodingPipeline:
    """
    Building and encapsulation helper for scikit-learn ColumnTransformer objects.
    Dynamically identifies feature categories and builds data validation-ready encoders.
    """

    def __init__(self, categorical_cols: List[str] = None, numeric_cols: List[str] = None, boolean_cols: List[str] = None):
        """
        Initializes EncodingPipeline with optional column type lists.
        If not provided, column types will be dynamically inferred during build_pipeline.
        """
        self.categorical_cols = categorical_cols
        self.numeric_cols = numeric_cols
        self.boolean_cols = boolean_cols
        self.transformer: ColumnTransformer = None

    def infer_column_types(self, df: pd.DataFrame) -> Tuple[List[str], List[str], List[str]]:
        """
        Infers column types from DataFrame to group them into numeric, categorical, and binary/boolean.

        Args:
            df: Input feature DataFrame.

        Returns:
            Tuple of lists: (numeric_cols, categorical_cols, boolean_cols)
        """
        cat_list = []
        bool_list = []
        num_list = []

        for col in df.columns:
            dtype = df[col].dtype
            # Categorical inference
            if isinstance(dtype, pd.CategoricalDtype) or dtype == object:
                cat_list.append(col)
                continue
            
            # Boolean/Binary flag inference
            unique_vals = df[col].dropna().unique()
            is_binary = (
                len(unique_vals) <= 2 
                and all(val in [0, 1, 0.0, 1.0, True, False] for val in unique_vals)
            )

            if dtype == bool or is_binary:
                bool_list.append(col)
            else:
                num_list.append(col)

        logger.info(
            "Inferred column groupings: %d Numeric, %d Categorical, %d Boolean/Binary",
            len(num_list),
            len(cat_list),
            len(bool_list),
        )
        return num_list, cat_list, bool_list

    def build_pipeline(self, X_train: pd.DataFrame) -> ColumnTransformer:
        """
        Builds and configures ColumnTransformer using dynamic type extraction from X_train.

        Args:
            X_train: Training feature DataFrame.

        Returns:
            ColumnTransformer: Complete un-fit scikit-learn pipeline transformer.
        """
        logger.info("Building ColumnTransformer encoding pipeline.")

        # 1. Infer column categories if not defined
        num_cols = self.numeric_cols
        cat_cols = self.categorical_cols
        bool_cols = self.boolean_cols

        if num_cols is None or cat_cols is None or bool_cols is None:
            inferred_num, inferred_cat, inferred_bool = self.infer_column_types(X_train)
            num_cols = num_cols or inferred_num
            cat_cols = cat_cols or inferred_cat
            bool_cols = bool_cols or inferred_bool

        self.numeric_cols = num_cols
        self.categorical_cols = cat_cols
        self.boolean_cols = bool_cols

        # 2. Build type-specific sub-pipelines
        logger.info("Creating sub-pipelines for each column type.")
        
        # Numeric pipeline: impute with median, no scaling
        num_transformer = Pipeline(steps=[
            ("imputer", SimpleImputer(strategy="median"))
        ])

        # Categorical pipeline: impute and OHE
        cat_transformer = Pipeline(steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore", drop=None, sparse_output=False))
        ])

        # Binary/Boolean pipeline: impute with most frequent
        bool_transformer = Pipeline(steps=[
            ("imputer", SimpleImputer(strategy="most_frequent"))
        ])

        # 3. Construct ColumnTransformer
        transformers = []
        if num_cols:
            transformers.append(("num", num_transformer, num_cols))
        if cat_cols:
            transformers.append(("cat", cat_transformer, cat_cols))
        if bool_cols:
            transformers.append(("bool", bool_transformer, bool_cols))

        preprocessor = ColumnTransformer(
            transformers=transformers,
            remainder="drop"
        )

        # Set to output pandas DataFrame
        try:
            preprocessor.set_output(transform="pandas")
        except Exception as e:
            logger.warning("Could not set_output to pandas on ColumnTransformer. Error: %s", e)

        self.transformer = preprocessor
        return preprocessor
