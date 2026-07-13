"""
Validation schemas for the Claims module.
Defines schemas using Pydantic to validate policy claim forms.
"""

from typing import Optional
from pydantic import BaseModel, Field, field_validator, StringConstraints
from typing_extensions import Annotated


class ClaimInputValidator(BaseModel):
    """
    Validates structural parameters of claim reports before dispatching to the underwriter log.
    """
    claim_id: Optional[str] = Field(default=None, description="Auto-generated unique tracking uuid")
    policy_number: Annotated[str, StringConstraints(min_length=5, max_length=50)] = Field(
        ..., description="Active insurance policy identifier, e.g. POL-12345"
    )
    vehicle_type: str = Field(..., description="Vehicle segment type classification")
    description: Annotated[str, StringConstraints(min_length=10, max_length=2000)] = Field(
        ..., description="Comprehensive explanation of incident damage details"
    )
    claim_amount: float = Field(..., ge=100.0, le=5000000.0, description="Amount claimed for coverage repairs in INR")

    @field_validator("policy_number")
    @classmethod
    def check_policy_prefix(cls, val: str) -> str:
        """Verifies policy numbers follow structured standards."""
        cleaned = val.strip().upper()
        if not cleaned:
            raise ValueError("Policy number cannot be blank.")
        return cleaned
