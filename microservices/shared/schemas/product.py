"""Shared product schemas used across microservices."""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ProductBase(BaseModel):
    """Base product schema."""
    product_id: str = Field(..., description="Unique product identifier")
    name: str = Field(..., description="Product name")
    price: float = Field(..., gt=0, description="Product price")
    tax_percentage: float = Field(..., ge=0, le=100, description="Tax percentage")
    available_stock: int = Field(..., ge=0, description="Available stock quantity")


class ProductCreate(ProductBase):
    """Schema for creating a product."""
    pass


class ProductUpdate(BaseModel):
    """Schema for updating a product."""
    name: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    tax_percentage: Optional[float] = Field(None, ge=0, le=100)
    available_stock: Optional[int] = Field(None, ge=0)


class ProductResponse(ProductBase):
    """Schema for product response."""
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class StockCheckRequest(BaseModel):
    """Request to check product stock."""
    product_id: str
    quantity: int = Field(..., gt=0)


class StockCheckResponse(BaseModel):
    """Response for stock check."""
    product_id: str
    available: bool
    available_stock: int
    requested_quantity: int


class StockUpdateRequest(BaseModel):
    """Request to update product stock."""
    product_id: str
    quantity_change: int  # Positive to add, negative to reduce
