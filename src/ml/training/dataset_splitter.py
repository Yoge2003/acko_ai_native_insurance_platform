"""
Dataset Splitter.
Splits data into train (70%), validation (15%), and test (15%) sets.
Applies stratification for classification targets.
"""

import logging
from typing import Tuple
import pandas as pd
from sklearn.model_selection import train_test_split

# Set up logger
logger = logging.getLogger(__name__)


class DatasetSplitter:
    """
    Splitter utility for dividing features and labels into training, validation, and test splits.
    Supports stratified splits for classification datasets to prevent class imbalance issues.
    """

    @staticmethod
    def split(
        X: pd.DataFrame, y: pd.Series, stratify: bool = False, random_state: int = 42
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.Series, pd.Series, pd.Series]:
        """
        Splits features and target into train (70%), validation (15%), and test (15%) allocations.

        Args:
            X: Input features DataFrame.
            y: Target labels Series.
            stratify: Whether to perform stratified split (use for classification).
            random_state: Random seed for reproducibility.

        Returns:
            Tuple containing:
                X_train, X_valid, X_test, y_train, y_valid, y_test
        """
        logger.info(
            "Splitting dataset. Shape: X=%s, y=%s. Stratified: %s",
            X.shape,
            y.shape,
            stratify,
        )

        # 1. First split: 70% Train, 30% Temp (Val + Test)
        stratify_labels = y if stratify else None
        
        X_train, X_temp, y_train, y_temp = train_test_split(
            X,
            y,
            test_size=0.30,
            random_state=random_state,
            stratify=stratify_labels,
        )

        # 2. Second split: split Temp half-half (15% Validation, 15% Test)
        stratify_temp_labels = y_temp if stratify else None
        X_valid, X_test, y_valid, y_test = train_test_split(
            X_temp,
            y_temp,
            test_size=0.50,
            random_state=random_state,
            stratify=stratify_temp_labels,
        )

        logger.info(
            "Split statistics: "
            "Train: %d rows (%.1f%%), "
            "Valid: %d rows (%.1f%%), "
            "Test: %d rows (%.1f%%)",
            len(X_train),
            (len(X_train) / len(X)) * 100,
            len(X_valid),
            (len(X_valid) / len(X)) * 100,
            len(X_test),
            (len(X_test) / len(X)) * 100,
        )

        return X_train, X_valid, X_test, y_train, y_valid, y_test
