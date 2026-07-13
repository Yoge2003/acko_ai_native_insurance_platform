"""
Configuration module for the ACKO AI Native Insurance Platform.
Exposes settings, constants, and logging setup.
"""

from src.config.settings import settings
from src.config.constants import (
    APP_NAME,
    APP_VERSION,
    SUPPORTED_VEHICLE_TYPES,
    SUPPORTED_POLICY_TYPES,
    ALLOWED_IMAGE_EXTENSIONS,
    ALLOWED_PDF_EXTENSIONS,
    MAX_FILE_SIZE_MB,
)

__all__ = [
    "settings",
    "APP_NAME",
    "APP_VERSION",
    "SUPPORTED_VEHICLE_TYPES",
    "SUPPORTED_POLICY_TYPES",
    "ALLOWED_IMAGE_EXTENSIONS",
    "ALLOWED_PDF_EXTENSIONS",
    "MAX_FILE_SIZE_MB",
]
