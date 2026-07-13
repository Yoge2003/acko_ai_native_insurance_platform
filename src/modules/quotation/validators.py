"""
Validation schemas for the Premium Quotation module.
Defines schemas using Pydantic to validate policy underwriting and premium parameters.
"""

from datetime import datetime
from pydantic import BaseModel, Field, field_validator, StringConstraints
from typing_extensions import Annotated
from src.utils.validators import is_valid_phone


class QuotationInputValidator(BaseModel):
    """
    Validates structural constraints of quotation parameters before premium calculation.
    """
    customer_name: Annotated[str, StringConstraints(min_length=2, max_length=100)] = Field(
        ..., description="First and Last name of the customer"
    )
    age: int = Field(..., ge=18, le=110, description="Age of the vehicle driver")
    gender: str = Field(..., description="Gender identifier of the vehicle driver")
    mobile_number: str = Field(..., description="E.164 phone representation")
    
    vehicle_type: str = Field(..., description="Category classification: Car or Two-Wheeler (Bike)")
    manufacturer: str = Field(..., min_length=1, description="Brand manufacturer name")
    model: str = Field(..., min_length=1, description="Specific vehicle model model description")
    fuel_type: str = Field(..., description="Propulsion type: Petrol, Diesel, CNG, or Electric")
    manufacturing_year: int = Field(..., ge=2000, description="Calendar year of vehicle construction")
    
    city: str = Field(..., min_length=1, description="Operational city location")
    state: str = Field(..., min_length=2, description="Admin territory state location")
    vehicle_idv: float = Field(..., ge=5000.0, le=10000000.0, description="Insured Declared Value (IDV) of the vehicle in INR")
    ncb_percentage: int = Field(default=0, ge=0, le=50, description="Eligible No Claim Bonus (NCB) percentile rate")
    previous_claims: bool = Field(default=False, description="Whether claims were lodged in prior terms")

    @field_validator("mobile_number")
    @classmethod
    def check_phone_number(cls, v: str) -> str:
        """Verifies that the phone number matches active format constraints."""
        if not is_valid_phone(v):
            raise ValueError("Mobile number must be a valid E.164 phone string (e.g., +919876543210).")
        return v

    @field_validator("manufacturing_year")
    @classmethod
    def check_year_not_future(cls, v: int) -> int:
        """Confirms that manufacturing year is not in the future relative to the current year."""
        current_year = datetime.now().year
        if v > current_year:
            raise ValueError(f"Manufacturing year '{v}' cannot exceed current year: {current_year}.")
        return v
