from pydantic import BaseModel
from datetime import datetime
from typing import List


class OrderItemResponse(BaseModel):
    product_id: int
    product_name: str
    quantity: int
    unit_price: float
    tax_amount: float
    total_price: float

    class Config:
        from_attributes = True


class OrderResponse(BaseModel):
    id: int
    customer_email: str

    total_without_tax: float
    total_tax: float
    total_amount: float

    paid_amount: float
    balance_amount: float

    created_at: datetime

    items: List[OrderItemResponse]

    class Config:
        from_attributes = True
