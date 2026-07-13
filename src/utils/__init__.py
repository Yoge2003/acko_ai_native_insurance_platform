"""
Utilities module for sharing common helper functions, validation shortcuts, and document utilities.
"""

from src.utils.helpers import format_currency, calculate_percentage, log_execution_time
from src.utils.validators import is_valid_email, is_valid_phone, is_valid_vehicle_registration
from src.utils.file_utils import get_file_extension, is_allowed_file, get_pdf_page_count
from src.utils.common import generate_uuid, serialize_datetime

__all__ = [
    "format_currency",
    "calculate_percentage",
    "log_execution_time",
    "is_valid_email",
    "is_valid_phone",
    "is_valid_vehicle_registration",
    "get_file_extension",
    "is_allowed_file",
    "get_pdf_page_count",
    "generate_uuid",
    "serialize_datetime",
]
