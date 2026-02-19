"""Denomination Service FastAPI application."""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import sys
from pathlib import Path

# Add parent directory to path for shared modules
parent_dir = str(Path(__file__).parent.parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from shared.schemas.denomination import (
    DenominationCreate,
    DenominationUpdate,
    DenominationResponse,
    CalculateChangeRequest,
    CalculateChangeResponse
)
from .database import get_db, engine, Base
from .models import Denomination
from .config import settings

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Denomination Service",
    description="Microservice for denomination management and change calculation",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": settings.SERVICE_NAME}


@app.post("/denominations", response_model=DenominationResponse, status_code=status.HTTP_201_CREATED)
async def create_denomination(denomination: DenominationCreate, db: Session = Depends(get_db)):
    """Create a new denomination."""
    # Check if denomination value already exists
    existing = db.query(Denomination).filter(Denomination.value == denomination.value).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Denomination with value {denomination.value} already exists"
        )
    
    db_denomination = Denomination(**denomination.model_dump())
    db.add(db_denomination)
    db.commit()
    db.refresh(db_denomination)
    return db_denomination


@app.get("/denominations", response_model=List[DenominationResponse])
async def get_denominations(db: Session = Depends(get_db)):
    """Get all denominations sorted by value (descending)."""
    denominations = db.query(Denomination).order_by(Denomination.value.desc()).all()
    return denominations


@app.get("/denominations/{denomination_id}", response_model=DenominationResponse)
async def get_denomination(denomination_id: int, db: Session = Depends(get_db)):
    """Get a specific denomination by ID."""
    denomination = db.query(Denomination).filter(Denomination.id == denomination_id).first()
    if not denomination:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Denomination with ID {denomination_id} not found"
        )
    return denomination


@app.put("/denominations/{denomination_id}", response_model=DenominationResponse)
async def update_denomination(
    denomination_id: int,
    denomination_update: DenominationUpdate,
    db: Session = Depends(get_db)
):
    """Update a denomination's available count."""
    db_denomination = db.query(Denomination).filter(Denomination.id == denomination_id).first()
    if not db_denomination:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Denomination with ID {denomination_id} not found"
        )
    
    update_data = denomination_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_denomination, field, value)
    
    db.commit()
    db.refresh(db_denomination)
    return db_denomination


@app.delete("/denominations/{denomination_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_denomination(denomination_id: int, db: Session = Depends(get_db)):
    """Delete a denomination."""
    db_denomination = db.query(Denomination).filter(Denomination.id == denomination_id).first()
    if not db_denomination:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Denomination with ID {denomination_id} not found"
        )
    
    db.delete(db_denomination)
    db.commit()
    return None


@app.post("/denominations/calculate-change", response_model=CalculateChangeResponse)
async def calculate_change(request: CalculateChangeRequest, db: Session = Depends(get_db)):
    """
    Calculate optimal change denominations using greedy algorithm.
    
    Returns the denominations needed to make up the requested amount,
    respecting available counts.
    """
    amount = int(request.amount)
    if amount <= 0:
        return CalculateChangeResponse(
            amount=0,
            denominations={},
            total_returned=0,
            shortfall=0
        )
    
    # Get all denominations sorted by value (descending)
    denominations = db.query(Denomination).order_by(Denomination.value.desc()).all()
    
    remaining = amount
    result = {}
    
    for denom in denominations:
        if remaining <= 0:
            break
        
        # Calculate maximum notes/coins we can use
        usable_count = min(
            remaining // denom.value,
            denom.available_count
        )
        
        if usable_count > 0:
            result[denom.value] = usable_count
            remaining -= denom.value * usable_count
    
    total_returned = amount - remaining
    
    return CalculateChangeResponse(
        amount=request.amount,
        denominations=result,
        total_returned=float(total_returned),
        shortfall=float(remaining)
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.SERVICE_PORT)
