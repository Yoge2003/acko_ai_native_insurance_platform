"""
Data loader module for loading raw CSV datasets in the ACKO AI Native Insurance Platform.
"""

import os
import logging
from pathlib import Path
from typing import Union
import pandas as pd

# Set up logger
logger = logging.getLogger(__name__)


class DataLoader:
    """
    Utility class for loading dataset CSV files into Pandas DataFrames.
    Ensures safe reads and raises descriptive errors if files are missing.
    """

    @staticmethod
    def get_project_root() -> Path:
        """
        Retrieves the absolute path to the project root directory.

        Returns:
            Path: The project root directory Path object.
        """
        # Resolves to project root: .../acko_ai_native_insurance_platform
        return Path(__file__).resolve().parent.parent.parent.parent

    @classmethod
    def find_file_path(cls, filename: str) -> Path:
        """
        Locates the specified file in the workspace or datasets directories.

        Args:
            filename: The name of the CSV file or a path.

        Returns:
            Path: Located absolute path to the CSV file.

        Raises:
            FileNotFoundError: If the file cannot be located.
        """
        root = cls.get_project_root()
        path_candidate = Path(filename)

        # 1. Check if direct path is absolute and exists
        if path_candidate.is_absolute() and path_candidate.exists():
            return path_candidate

        # 2. Check direct path relative to project root
        proj_rel_path = root / path_candidate
        if proj_rel_path.exists():
            return proj_rel_path.resolve()

        # 3. Check specific subdirectories under DataSet and datasets folders
        search_dirs = [
            root / "DataSet" / "claim_Quotation_datas" / "Quotation",
            root / "DataSet" / "claim_Quotation_datas" / "Claims",
            root / "datasets",
            root / "DataSet",
            root,
        ]

        for s_dir in search_dirs:
            candidate = s_dir / path_candidate.name
            if candidate.exists():
                logger.info("Found dataset file at: %s", candidate)
                return candidate.resolve()

        # Raise exception if search exhausted and file not found
        error_msg = f"Dataset file '{filename}' not found. Searched in: {[str(d) for d in search_dirs]}"
        logger.error(error_msg)
        raise FileNotFoundError(error_msg)

    @classmethod
    def load_csv(cls, filename: str, **kwargs) -> pd.DataFrame:
        """
        Loads a CSV file by resolving its location and reading it into a Pandas DataFrame.
        Guarantees that the original dataset file remains unmodified.

        Args:
            filename: The filename or path of the CSV dataset to load.
            **kwargs: Extra parameters to pass to pandas.read_csv().

        Returns:
            pd.DataFrame: Loaded DataFrame.

        Raises:
            FileNotFoundError: If the file is not found.
            IOError: If reading the CSV fails.
        """
        file_path = cls.find_file_path(filename)
        logger.info("Loading dataset from: %s", file_path)
        try:
            # Load CSV using pandas and return copy to guarantee original remains untouched
            df = pd.read_csv(file_path, **kwargs)
            logger.info("Loaded shape: %s from file: %s", df.shape, file_path.name)
            return df.copy()
        except Exception as e:
            error_msg = f"Failed to read CSV file '{file_path}'. Error: {str(e)}"
            logger.error(error_msg)
            raise IOError(error_msg) from e
