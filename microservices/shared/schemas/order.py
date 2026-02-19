"""Shared order schemas used across microservices."""

from pydantic import BaseModel, Field, EmailStr
from typing import List, Dict, Optional
from datetime import datetime


class OrderItemBase(BaseModel):
    """Base order item schema."""
    product_id: str = Field(..., description="Product identifier")
    quantity: int = Field(..., gt=0, description="Quantity ordered")


class BillingItem(OrderItemBase):
    """Item in billing request."""
    pass


class BillingRequest(BaseModel):
    """Request to create a bill/order."""
    customer_email: EmailStr = Field(..., description="Customer email address")
    items: List[BillingItem] = Field(..., min_length=1, description="List of items to purchase")
    paid_amount: float = Field(..., gt=0, description="Amount paid by customer")


class OrderItemDetail(BaseModel):
    """Detailed order item information."""
    product_id: str
    product_name: str
    quantity: int
    unit_price: float
    tax_amount: float
    total_price: float


class BillingResponse(BaseModel):
    """Response after creating a bill."""
    order_id: int
    customer_email: str
    total_without_tax: float
    total_tax: float
    total_amount: float
    paid_amount: float
    balance_amount: float
    balance_denominations: Dict[int, int]


class OrderResponse(BaseModel):
    """Order details response."""
    id: int
    customer_email: str
    total_without_tax: float
    total_tax: float
    total_amount: float
    paid_amount: float
    balance_amount: float
    created_at: datetime
    items: Optional[List[OrderItemDetail]] = None
    
    class Config:
        from_attributes = True
