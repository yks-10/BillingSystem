"""Product Service FastAPI application."""

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

from shared.schemas.product import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    StockCheckRequest,
    StockCheckResponse,
    StockUpdateRequest
)
from .database import get_db, engine, Base
from .models import Product
from .config import settings

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Product Service",
    description="Microservice for product management",
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


@app.post("/products", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    """Create a new product."""
    # Check if product_id already exists
    existing = db.query(Product).filter(Product.product_id == product.product_id).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Product with ID '{product.product_id}' already exists"
        )
    
    db_product = Product(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


@app.get("/products", response_model=List[ProductResponse])
async def get_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all products with pagination."""
    products = db.query(Product).offset(skip).limit(limit).all()
    return products


@app.get("/products/{product_id}", response_model=ProductResponse)
async def get_product(product_id: str, db: Session = Depends(get_db)):
    """Get a specific product by product_id."""
    product = db.query(Product).filter(Product.product_id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product '{product_id}' not found"
        )
    return product


@app.put("/products/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: str,
    product_update: ProductUpdate,
    db: Session = Depends(get_db)
):
    """Update an existing product."""
    db_product = db.query(Product).filter(Product.product_id == product_id).first()
    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product '{product_id}' not found"
        )
    
    update_data = product_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_product, field, value)
    
    db.commit()
    db.refresh(db_product)
    return db_product


@app.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(product_id: str, db: Session = Depends(get_db)):
    """Delete a product."""
    db_product = db.query(Product).filter(Product.product_id == product_id).first()
    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product '{product_id}' not found"
        )
    
    db.delete(db_product)
    db.commit()
    return None


@app.post("/products/check-stock", response_model=StockCheckResponse)
async def check_stock(request: StockCheckRequest, db: Session = Depends(get_db)):
    """Check if sufficient stock is available for a product."""
    product = db.query(Product).filter(Product.product_id == request.product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product '{request.product_id}' not found"
        )
    
    available = product.available_stock >= request.quantity
    return StockCheckResponse(
        product_id=request.product_id,
        available=available,
        available_stock=product.available_stock,
        requested_quantity=request.quantity
    )


@app.post("/products/update-stock")
async def update_stock(request: StockUpdateRequest, db: Session = Depends(get_db)):
    """Update product stock (positive to add, negative to reduce)."""
    product = db.query(Product).filter(Product.product_id == request.product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product '{request.product_id}' not found"
        )
    
    new_stock = product.available_stock + request.quantity_change
    if new_stock < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Insufficient stock. Available: {product.available_stock}, Requested reduction: {abs(request.quantity_change)}"
        )
    
    product.available_stock = new_stock
    db.commit()
    db.refresh(product)
    
    return {
        "product_id": product.product_id,
        "previous_stock": product.available_stock - request.quantity_change,
        "current_stock": product.available_stock,
        "change": request.quantity_change
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.SERVICE_PORT)
