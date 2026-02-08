from pydantic import BaseModel
from typing import Optional


class DenominationCreate(BaseModel):
    value: int
    available_count: int = 0


class DenominationUpdate(BaseModel):
    available_count: Optional[int] = None


class DenominationResponse(BaseModel):
    id: int
    value: int
    available_count: int

    class Config:
        from_attributes = True
