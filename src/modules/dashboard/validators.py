"""
Validation schemas for the Analytics Dashboard module.
Defines schemas using Pydantic to validate visualization filters and reports parameters.
"""

from typing import Optional
from pydantic import BaseModel, Field


class DashboardFilterValidator(BaseModel):
    """
    Validates range selections and segmentation codes placed on the executive reporting dashboard.
    """
    days_range: int = Field(default=30, ge=1, le=365, description="Time scale window in elapsed days")
    segment: Optional[str] = Field(default="All", description="Policy segment class filter (e.g. Car, Two-Wheeler, All)")
