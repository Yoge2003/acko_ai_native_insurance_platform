"""
Global application constants for the ACKO AI Native Insurance Platform.
Defines static configurations, allowed file uploads, size caps, and domain terms.
"""

from typing import List, Set

# ── Application Metadata ──────────────────────────────────────────────────────
APP_NAME: str = "ACKO AI Native Insurance Platform"
APP_VERSION: str = "1.0.0"

# ── Supported Insurance Entities ──────────────────────────────────────────────
# Supported categories for quoting and claims
SUPPORTED_VEHICLE_TYPES: List[str] = [
    "Car",
    "Two-Wheeler (Bike)",
]

# Supported insurance coverage plans
SUPPORTED_POLICY_TYPES: List[str] = [
    "Comprehensive Insurance",
    "Third-Party Liability Only",
    "Own Damage Policy",
]

# ── File Upload Validations ───────────────────────────────────────────────────
# Size limits and validation extensions for claiming documents, visual repairs
MAX_FILE_SIZE_MB: int = 15  # Maximum size of individual uploaded files in Megabytes
ALLOWED_IMAGE_EXTENSIONS: Set[str] = {"png", "jpg", "jpeg", "webp"}
ALLOWED_PDF_EXTENSIONS: Set[str] = {"pdf"}

# ── Business Flow Defaults ────────────────────────────────────────────────────
DEFAULT_CURRENCY: str = "INR"
DEFAULT_COUNTRY_CODE: str = "IN"

# Machine Learning configuration identifiers
MODEL_EVAL_METRICS: List[str] = ["RMSE", "MAE", "R2", "MAPE"]

# Session validation details
SESSION_TIMEOUT_MINUTES: int = 60
