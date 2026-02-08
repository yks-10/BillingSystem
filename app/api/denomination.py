from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.models.denomination import Denomination
from app.schemas.denomination import (
    DenominationCreate,
    DenominationUpdate,
    DenominationResponse
)

router = APIRouter(
    prefix="/denominations",
    tags=["Denominations"]
)


@router.post("/", response_model=DenominationResponse, status_code=status.HTTP_201_CREATED)
async def create_denomination(
    denomination: DenominationCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new denomination.
    
    Args:
        denomination: Denomination data
        db: Database session
        
    Returns:
        Created denomination
        
    Raises:
        HTTPException: If denomination value already exists
    """
    # Check if denomination value already exists
    existing = db.query(Denomination).filter(
        Denomination.value == denomination.value
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Denomination of ₹{denomination.value} already exists"
        )
    
    db_denomination = Denomination(**denomination.model_dump())
    db.add(db_denomination)
    db.commit()
    db.refresh(db_denomination)
    
    return db_denomination


@router.get("/", response_model=List[DenominationResponse])
async def get_all_denominations(
    db: Session = Depends(get_db)
):
    """
    Get all denominations ordered by value descending.
    
    Args:
        db: Database session
        
    Returns:
        List of all denominations
    """
    denominations = (
        db.query(Denomination)
        .order_by(Denomination.value.desc())
        .all()
    )
    return denominations


@router.get("/{denomination_id}", response_model=DenominationResponse)
async def get_denomination(
    denomination_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific denomination by ID.
    
    Args:
        denomination_id: Denomination ID
        db: Database session
        
    Returns:
        Denomination details
        
    Raises:
        HTTPException: If denomination not found
    """
    denomination = db.query(Denomination).filter(
        Denomination.id == denomination_id
    ).first()
    
    if not denomination:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Denomination with ID {denomination_id} not found"
        )
    
    return denomination


@router.put("/{denomination_id}", response_model=DenominationResponse)
async def update_denomination(
    denomination_id: int,
    denomination_update: DenominationUpdate,
    db: Session = Depends(get_db)
):
    """
    Update denomination available count.
    
    Args:
        denomination_id: Denomination ID
        denomination_update: Updated count
        db: Database session
        
    Returns:
        Updated denomination
        
    Raises:
        HTTPException: If denomination not found
    """
    db_denomination = db.query(Denomination).filter(
        Denomination.id == denomination_id
    ).first()
    
    if not db_denomination:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Denomination with ID {denomination_id} not found"
        )
    
    # Update only the available_count
    update_data = denomination_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_denomination, field, value)
    
    db.commit()
    db.refresh(db_denomination)
    
    return db_denomination


@router.put("/value/{value}", response_model=DenominationResponse)
async def update_denomination_by_value(
    value: int,
    denomination_update: DenominationUpdate,
    db: Session = Depends(get_db)
):
    """
    Update denomination available count by value.
    
    Args:
        value: Denomination value (e.g., 100, 500)
        denomination_update: Updated count
        db: Database session
        
    Returns:
        Updated denomination
        
    Raises:
        HTTPException: If denomination not found
    """
    db_denomination = db.query(Denomination).filter(
        Denomination.value == value
    ).first()
    
    if not db_denomination:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Denomination of ₹{value} not found"
        )
    
    # Update only the available_count
    update_data = denomination_update.model_dump(exclude_unset=True)
    for field, value_update in update_data.items():
        setattr(db_denomination, field, value_update)
    
    db.commit()
    db.refresh(db_denomination)
    
    return db_denomination


@router.delete("/{denomination_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_denomination(
    denomination_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a denomination.
    
    Args:
        denomination_id: Denomination ID
        db: Database session
        
    Raises:
        HTTPException: If denomination not found
    """
    db_denomination = db.query(Denomination).filter(
        Denomination.id == denomination_id
    ).first()
    
    if not db_denomination:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Denomination with ID {denomination_id} not found"
        )
    
    db.delete(db_denomination)
    db.commit()
    
    return None
