from pydantic import BaseModel, EmailStr
from typing import List, Dict


class BillingItem(BaseModel):
    product_id: str
    quantity: int


class BillingRequest(BaseModel):
    customer_email: EmailStr
    items: List[BillingItem]
    paid_amount: float


class BillingResponse(BaseModel):
    order_id: int
    customer_email: str

    total_without_tax: float
    total_tax: float
    total_amount: float

    paid_amount: float
    balance_amount: float

    balance_denominations: Dict[int, int]
