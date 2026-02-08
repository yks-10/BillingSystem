from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ProductCreate(BaseModel):
    product_id: str
    name: str
    price: float
    tax_percentage: float
    available_stock: int


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    tax_percentage: Optional[float] = None
    available_stock: Optional[int] = None


class ProductResponse(BaseModel):
    id: int
    product_id: str
    name: str
    price: float
    tax_percentage: float
    available_stock: int
    created_at: datetime

    class Config:
        from_attributes = True
