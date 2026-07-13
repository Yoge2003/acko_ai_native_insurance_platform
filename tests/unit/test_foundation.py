"""
Baseline unit tests to verify configuration parameters, helpers, and validators.
Validates the structural setup of Phase 3.1.
"""

from src.config.constants import APP_NAME, SUPPORTED_VEHICLE_TYPES
from src.utils.helpers import format_currency, calculate_percentage
from src.utils.validators import is_valid_email, is_valid_phone, is_valid_vehicle_registration
from src.utils.common import generate_uuid, serialize_datetime, clean_dictionary


def test_app_constants() -> None:
    """Verifies default application configuration constants."""
    assert APP_NAME == "ACKO AI Native Insurance Platform"
    assert "Car" in SUPPORTED_VEHICLE_TYPES
    assert "Two-Wheeler (Bike)" in SUPPORTED_VEHICLE_TYPES


def test_helpers_format_and_math() -> None:
    """Verifies helper formatting and mathematically safe functions."""
    assert format_currency(12897) == "₹12,897.00"
    assert format_currency(0) == "₹0.00"
    assert calculate_percentage(20, 100) == 20.0
    assert calculate_percentage(5, 0) == 0.0  # Safe division check


def test_validators_format() -> None:
    """Verifies that format validators correctly check structural strings."""
    assert is_valid_email("developer@acko-insurance.in") is True
    assert is_valid_email("not_an_email") is False
    assert is_valid_phone("+919999988888") is True
    # Test vehicle registration formats
    assert is_valid_vehicle_registration("MH-12-AB-1234") is True
    assert is_valid_vehicle_registration("DL3CA9999") is True
    assert is_valid_vehicle_registration("invalid-reg-num") is False


def test_common_utils() -> None:
    """Verifies UUID generators and dictionary cleaners."""
    uuid_str = generate_uuid()
    assert len(uuid_str) == 36
    
    dirty_dict = {" name ": " Acko ", "age": None, "plan": "comprehensive"}
    cleaned = clean_dictionary(dirty_dict)
    assert "name" in cleaned
    assert "age" not in cleaned

