from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Dict

from app.core.database import get_db
from app.schemas.billing import BillingRequest, BillingResponse
from app.services.billing_service import generate_bill

router = APIRouter(
    prefix="/billing",
    tags=["Billing"]
)


@router.post("/", response_model=BillingResponse, status_code=status.HTTP_201_CREATED)
async def create_bill(
    billing_data: BillingRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Create a new bill/order.
    
    This endpoint:
    - Validates product availability and stock
    - Calculates taxes and totals
    - Creates order and order items
    - Updates product stock
    - Calculates change denominations
    - Sends invoice email asynchronously
    
    Args:
        billing_data: Billing request containing customer email, items, and paid amount
        background_tasks: FastAPI background tasks for async email sending
        db: Database session
        
    Returns:
        BillingResponse with order details, totals, and change denominations
        
    Raises:
        HTTPException: If product not found, insufficient stock, or insufficient payment
    """
    try:
        result = generate_bill(db, billing_data, background_tasks)
        return result
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
