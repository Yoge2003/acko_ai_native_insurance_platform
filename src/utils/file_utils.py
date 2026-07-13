"""
File utility functions.
Details file size constraints, file path validation, and PDF inspection.
No business logic contains herein.
"""

import os
import logging
from pathlib import Path
from typing import Set, Union

logger = logging.getLogger(__name__)

# Attempt to load optional dependencies for robust PDF integration
try:
    import fitz  # PyMuPDF
    HAS_PYMUPDF = True
except ImportError:
    HAS_PYMUPDF = False
    logger.warning("PyMuPDF (fitz) is not available. Will fallback to other methods for PDF utilities.")

try:
    from pypdf import PdfReader
    HAS_PYPDF = True
except ImportError:
    HAS_PYPDF = False
    logger.warning("pypdf is not available. Please verify dependencies in requirements.txt.")


def get_file_extension(filename: str) -> str:
    """
    Returns the file extension in a clean, lowercase format without the leading dot.

    Args:
        filename: Base filename or full path.

    Returns:
        Extension string (e.g. 'pdf', 'png'). Returns empty string if no extension is found.
    """
    if not filename:
        return ""
    try:
        _, ext = os.path.splitext(filename)
        return ext.lstrip(".").lower()
    except Exception as err:
        logger.error(f"Error resolving extension for '{filename}': {err}")
        return ""


def is_allowed_file(filename: str, allowed_extensions: Set[str]) -> bool:
    """
    Verifies that the extension of a file belongs to a given allowed set.

    Args:
        filename: Name of the file.
        allowed_extensions: Set of valid lowercase strings (e.g., {'pdf', 'png'}).

    Returns:
        Boolean indicating validation success.
    """
    ext = get_file_extension(filename)
    return ext in allowed_extensions


def check_file_size(file_path: Union[str, Path], max_size_mb: float) -> bool:
    """
    Verifies if a file is below a specified path size limit in MB.

    Args:
        file_path: Path to the target physical file.
        max_size_mb: MegaBytes cap to validate.

    Returns:
        True if the file size is under the cap, False otherwise.
    """
    try:
        path = Path(file_path)
        if not path.is_file():
            logger.error(f"Target file for size check does not exist: {file_path}")
            return False
        
        file_size_bytes = path.stat().st_size
        file_size_mb = file_size_bytes / (1024 * 1024)
        return file_size_mb <= max_size_mb
    except Exception as err:
        logger.error(f"Error checking size of '{file_path}': {err}")
        return False


def get_pdf_page_count(file_path: Union[str, Path]) -> int:
    """
    Reads the page count of a PDF file using PyMuPDF (fitz) or PyPDF (PdfReader) as fallback.

    Args:
        file_path: Path to the physical PDF.

    Returns:
        Number of pages as an integer. Returns -1 if loading fails or files are unreadable.
    """
    path = Path(file_path)
    if not path.is_file():
        logger.error(f"PDF file for page count check does not exist: {path}")
        return -1

    # 1. Primary Option: PyMuPDF (faster and more memory efficient)
    if HAS_PYMUPDF:
        try:
            with fitz.open(str(path)) as doc:
                return len(doc)
        except Exception as err:
            logger.warning(f"PyMuPDF failed to read PDF '{file_path}': {err}. Trying fallback pypdf...")

    # 2. Secondary Option: PyPDF
    if HAS_PYPDF:
        try:
            reader = PdfReader(str(path))
            return len(reader.pages)
        except Exception as err:
            logger.error(f"pypdf failed to read PDF '{file_path}': {err}")

    # If all options failed or dependencies are not loaded
    logger.error(f"Failed to calculate page count for PDF '{file_path}' (Verify file formatting or package installations)")
    return -1
