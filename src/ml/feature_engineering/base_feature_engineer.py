"""
Base Feature Engineer.
Defines general helper methods, divisions-by-zero protection, categorical and day aggregators.
"""

import abc
import logging
from typing import List, Union
import numpy as np
import pandas as pd

# Set up logger
logger = logging.getLogger(__name__)


class BaseFeatureEngineer(abc.ABC):
    """
    Abstract base class for all feature engineers within the ACKO Insurance ML pipeline.
    Provides generic mathematical and temporal engineering helpers to prevent duplicated code.
    """

    def validate_dataframe(self, df: pd.DataFrame, expected_columns: List[str]) -> None:
        """
        Validates the input DataFrame checks.

        Args:
            df: The pd.DataFrame to validate.
            expected_columns: The columns that must exist in the DataFrame.

        Raises:
            ValueError: If df is empty, not a DataFrame, or missing expected columns.
        """
        if not isinstance(df, pd.DataFrame):
            error_msg = f"Expected pandas.DataFrame, got {type(df)}"
            logger.error(error_msg)
            raise ValueError(error_msg)

        if df.empty:
            error_msg = "DataFrame is empty."
            logger.error(error_msg)
            raise ValueError(error_msg)

        missing_cols = [col for col in expected_columns if col not in df.columns]
        if missing_cols:
            error_msg = f"DataFrame is missing columns required for engineering: {missing_cols}"
            logger.error(error_msg)
            raise ValueError(error_msg)

    def safe_divide(
        self, numerator: pd.Series, denominator: pd.Series, fill_value: float = 0.0
    ) -> pd.Series:
        """
        Safely divides two Series, protecting against division by zero.

        Args:
            numerator: The numerator Series.
            denominator: The denominator Series.
            fill_value: Value to return if denominator is zero or missing.

        Returns:
            pd.Series: Result of division.
        """
        # Replace zero with nan so pandas division handles it, then fill nans
        denom_cleaned = denominator.replace(0, np.nan)
        div = numerator / denom_cleaned
        return div.fillna(fill_value).astype(np.float64)

    def create_flag(self, condition_series: pd.Series) -> pd.Series:
        """
        Helper to convert a boolean series or condition to a binary indicator (np.int8).

        Args:
            condition_series: The boolean Series state.

        Returns:
            pd.Series: Binary Series containing values 0 or 1.
        """
        return condition_series.astype(np.int8)

    def extract_day(self, date_series: pd.Series, default_day: int = 15) -> pd.Series:
        """
        Safely extracts the day of the month from a date column.

        Args:
            date_series: date series containing date strings.
            default_day: fallback day to use on parsing errors.

        Returns:
            pd.Series: Parsed integer days (np.int32).
        """
        try:
            parsed_dates = pd.to_datetime(date_series, errors="coerce")
            return parsed_dates.dt.day.fillna(default_day).astype(np.int32)
        except Exception as e:
            logger.warning("Failed to parse date_series to datetime. Error: %s", e)
            return pd.Series(default_day, index=date_series.index).astype(np.int32)

    @abc.abstractmethod
    def fit_transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Abstract method to transform the preprocessed DataFrame into engineered state.

        Args:
            df: Cleaned preprocessed DataFrame.

        Returns:
            pd.DataFrame: DataFrame containing original columns and newly engineered features.
        """
        pass
