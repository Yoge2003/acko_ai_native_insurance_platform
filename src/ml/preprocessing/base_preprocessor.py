"""
Base Preprocessor class defining general data cleaning steps, standardizations,
validations, and helper methods for downstream portfolio preprocessing.
"""

import abc
import logging
from typing import List, Optional
import pandas as pd

# Set up logging
logger = logging.getLogger(__name__)


class BasePreprocessor(abc.ABC):
    """
    Abstract preprocessor class outlining the steps needed for cleaning, standardizing,
    and validating datasets in the Acko Insurance ML pipeline.
    """

    def __init__(self, required_columns: List[str]):
        """
        Initializes the preprocessor with a list of required columns.

        Args:
            required_columns: Columns that must be present in the input DataFrame.
        """
        self.required_columns = [col.strip().lower() for col in required_columns]

    def validate_dataframe(self, df: pd.DataFrame) -> None:
        """
        Checks if the input object is a valid DataFrame and logs initial checks.

        Args:
            df: The Pandas DataFrame to validate.

        Raises:
            ValueError: If input is not a DataFrame or is empty.
        """
        if not isinstance(df, pd.DataFrame):
            error_msg = f"Expected pandas.DataFrame, got {type(df)}"
            logger.error(error_msg)
            raise ValueError(error_msg)

        if df.empty:
            error_msg = "Input DataFrame is empty."
            logger.error(error_msg)
            raise ValueError(error_msg)

        logger.info("DataFrame validation passed: %d rows, %d columns.", len(df), len(df.columns))

    def standardize_column_names(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Standardizes column names of a DataFrame: strips whitespaces, converts to
        lowercase, and replaces spaces/hyphens with underscores.

        Args:
            df: The DataFrame whose columns need normalization.

        Returns:
            pd.DataFrame: A copy of the DataFrame with standardized column names.
        """
        logger.info("Standardizing DataFrame column names.")
        df_copy = df.copy()
        df_copy.columns = (
            df_copy.columns.str.strip()
            .str.lower()
            .str.replace(" ", "_")
            .str.replace("-", "_")
        )
        return df_copy

    def check_required_columns(self, df: pd.DataFrame) -> None:
        """
        Verifies that all required columns are present in the DataFrame.
        Assumes column names are already standardized.

        Args:
            df: The standardized DataFrame to check.

        Raises:
            ValueError: If any required column is missing.
        """
        missing_columns = [col for col in self.required_columns if col not in df.columns]
        if missing_columns:
            error_msg = f"Missing required columns in dataset: {missing_columns}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        logger.info("All required columns verified.")

    def remove_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Removes identical duplicate rows from the DataFrame.

        Args:
            df: The input DataFrame.

        Returns:
            pd.DataFrame: Cleaned DataFrame without duplicates.
        """
        logger.info("Checking for duplicate rows in DataFrame.")
        num_duplicates = df.duplicated().sum()
        if num_duplicates > 0:
            logger.warning("Found %d duplicate rows. Removing them.", num_duplicates)
            return df.drop_duplicates().reset_index(drop=True)
        else:
            logger.info("No duplicate rows found.")
            return df.copy()

    def drop_columns(self, df: pd.DataFrame, columns_to_drop: List[str]) -> pd.DataFrame:
        """
        Safely drops a list of columns from the DataFrame if they exist.

        Args:
            df: The input DataFrame.
            columns_to_drop: Columns to exclude.

        Returns:
            pd.DataFrame: Copy of DataFrame with target columns excluded.
        """
        logger.info("Pruning columns: %s", columns_to_drop)
        existing_drops = [col for col in columns_to_drop if col in df.columns]
        if existing_drops:
            df_dropped = df.drop(columns=existing_drops)
            logger.info("Dropped columns: %s", existing_drops)
            return df_dropped
        return df.copy()

    @abc.abstractmethod
    def preprocess(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Abstract method to be implemented by child preprocessors.
        Applies end-to-end cleaning and feature transformations.

        Args:
            df: Raw input DataFrame.

        Returns:
            pd.DataFrame: Cleaned and structured DataFrame ready for encoding/scaling.
        """
        pass
