"""Shared notification schemas used across microservices."""

from pydantic import BaseModel, EmailStr, Field
from typing import List, Dict, Optional


class EmailRecipient(BaseModel):
    """Email recipient information."""
    email: EmailStr
    name: Optional[str] = None


class InvoiceEmailRequest(BaseModel):
    """Request to send invoice email."""
    email_to: EmailStr
    order_id: int
    customer_email: str
    items: List[Dict]
    total_without_tax: float
    total_tax: float
    total_amount: float
    paid_amount: float
    balance_amount: float
    balance_denominations: Dict[int, int]


class GenericEmailRequest(BaseModel):
    """Request to send generic email."""
    recipients: List[EmailStr]
    subject: str
    body: str
    html: Optional[str] = None


class EmailResponse(BaseModel):
    """Email send response."""
    success: bool
    message: str
    email_id: Optional[str] = None
