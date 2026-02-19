"""Shared denomination schemas used across microservices."""

from pydantic import BaseModel, Field
from typing import Dict, Optional


class DenominationBase(BaseModel):
    """Base denomination schema."""
    value: int = Field(..., gt=0, description="Denomination value (e.g., 100, 500)")
    available_count: int = Field(..., ge=0, description="Number of notes/coins available")


class DenominationCreate(DenominationBase):
    """Schema for creating a denomination."""
    pass


class DenominationUpdate(BaseModel):
    """Schema for updating a denomination."""
    available_count: Optional[int] = Field(None, ge=0)


class DenominationResponse(DenominationBase):
    """Schema for denomination response."""
    id: int
    
    class Config:
        from_attributes = True


class CalculateChangeRequest(BaseModel):
    """Request to calculate change denominations."""
    amount: float = Field(..., gt=0, description="Amount to calculate change for")


class CalculateChangeResponse(BaseModel):
    """Response with calculated change."""
    amount: float
    denominations: Dict[int, int]
    total_returned: float
    shortfall: float = Field(default=0, description="Amount that couldn't be returned")
