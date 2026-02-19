"""Order Service FastAPI application."""

from fastapi import FastAPI, Depends, HTTPException, status, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Dict
import sys
from pathlib import Path

# Add parent directory to path for shared modules
parent_dir = str(Path(__file__).parent.parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from shared.schemas.order import (
    BillingRequest,
    BillingResponse,
    OrderResponse,
    OrderItemDetail
)
from shared.schemas.product import StockCheckRequest, StockUpdateRequest
from shared.schemas.denomination import CalculateChangeRequest
from shared.schemas.notification import InvoiceEmailRequest
from shared.utils.http_client import ServiceClient
from .database import get_db, engine, Base
from .models import Order, OrderItem
from .config import settings

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Order Service",
    description="Microservice for order processing and billing",
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

# Service clients
product_client = ServiceClient(settings.PRODUCT_SERVICE_URL)
denomination_client = ServiceClient(settings.DENOMINATION_SERVICE_URL)
notification_client = ServiceClient(settings.NOTIFICATION_SERVICE_URL)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": settings.SERVICE_NAME}


@app.post("/billing", response_model=BillingResponse, status_code=status.HTTP_201_CREATED)
async def create_bill(
    billing_data: BillingRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Create a new bill/order.
    
    This endpoint orchestrates multiple services:
    1. Product Service - Check stock and get product details
    2. Denomination Service - Calculate change
    3. Notification Service - Send invoice email
    """
    try:
        total_without_tax = 0
        total_tax = 0
        order_items_data = []
        
        # Step 1: Validate products and calculate totals
        for item in billing_data.items:
            # Get product details from Product Service
            product = await product_client.get(f"/products/{item.product_id}")
            
            # Check stock availability
            stock_check = await product_client.post(
                "/products/check-stock",
                json_data={
                    "product_id": item.product_id,
                    "quantity": item.quantity
                }
            )
            
            if not stock_check["available"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Insufficient stock for product {item.product_id}. Available: {stock_check['available_stock']}"
                )
            
            # Calculate prices
            purchase_price = product["price"] * item.quantity
            tax_amount = purchase_price * product["tax_percentage"] / 100
            total_price = purchase_price + tax_amount
            
            total_without_tax += purchase_price
            total_tax += tax_amount
            
            order_items_data.append({
                "product_id": product["product_id"],
                "product_name": product["name"],
                "quantity": item.quantity,
                "unit_price": product["price"],
                "tax_amount": tax_amount,
                "total_price": total_price
            })
        
        # Step 2: Validate payment
        total_amount = total_without_tax + total_tax
        balance_amount = billing_data.paid_amount - total_amount
        
        if balance_amount < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient payment. Total: ₹{total_amount:.2f}, Paid: ₹{billing_data.paid_amount:.2f}"
            )
        
        # Step 3: Calculate change denominations
        balance_denominations = {}
        if balance_amount > 0:
            change_response = await denomination_client.post(
                "/denominations/calculate-change",
                json_data={"amount": balance_amount}
            )
            balance_denominations = change_response["denominations"]
        
        # Step 4: Create order in database
        order = Order(
            customer_email=billing_data.customer_email,
            total_without_tax=total_without_tax,
            total_tax=total_tax,
            total_amount=total_amount,
            paid_amount=billing_data.paid_amount,
            balance_amount=balance_amount
        )
        
        db.add(order)
        db.flush()  # Get order.id before committing
        
        # Step 5: Create order items
        for item_data in order_items_data:
            order_item = OrderItem(
                order_id=order.id,
                product_id=item_data["product_id"],
                product_name=item_data["product_name"],
                quantity=item_data["quantity"],
                unit_price=item_data["unit_price"],
                tax_amount=item_data["tax_amount"],
                total_price=item_data["total_price"]
            )
            db.add(order_item)
        
        db.commit()
        db.refresh(order)
        
        # Step 6: Update product stock (in background to not block response)
        for item in billing_data.items:
            background_tasks.add_task(
                product_client.post,
                "/products/update-stock",
                json_data={
                    "product_id": item.product_id,
                    "quantity_change": -item.quantity
                }
            )
        
        # Step 7: Send invoice email (in background)
        email_items = []
        for item_data in order_items_data:
            email_items.append({
                "product_name": item_data["product_name"],
                "quantity": item_data["quantity"],
                "unit_price": item_data["unit_price"],
                "tax_amount": item_data["tax_amount"],
                "total_price": item_data["total_price"]
            })
        
        background_tasks.add_task(
            notification_client.post,
            "/notifications/email/invoice",
            json_data={
                "email_to": billing_data.customer_email,
                "order_id": order.id,
                "customer_email": billing_data.customer_email,
                "items": email_items,
                "total_without_tax": total_without_tax,
                "total_tax": total_tax,
                "total_amount": total_amount,
                "paid_amount": billing_data.paid_amount,
                "balance_amount": balance_amount,
                "balance_denominations": balance_denominations
            }
        )
        
        # Step 8: Return response
        return BillingResponse(
            order_id=order.id,
            customer_email=order.customer_email,
            total_without_tax=total_without_tax,
            total_tax=total_tax,
            total_amount=total_amount,
            paid_amount=billing_data.paid_amount,
            balance_amount=balance_amount,
            balance_denominations=balance_denominations
        )
        
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create order: {str(e)}"
        )


@app.get("/orders", response_model=List[OrderResponse])
async def get_orders(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all orders with pagination."""
    orders = db.query(Order).offset(skip).limit(limit).all()
    return orders


@app.get("/orders/{order_id}", response_model=OrderResponse)
async def get_order(order_id: int, db: Session = Depends(get_db)):
    """Get specific order with items."""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order {order_id} not found"
        )
    
    # Build response with items
    items = []
    for item in order.items:
        items.append(OrderItemDetail(
            product_id=item.product_id,
            product_name=item.product_name,
            quantity=item.quantity,
            unit_price=item.unit_price,
            tax_amount=item.tax_amount,
            total_price=item.total_price
        ))
    
    return OrderResponse(
        id=order.id,
        customer_email=order.customer_email,
        total_without_tax=order.total_without_tax,
        total_tax=order.total_tax,
        total_amount=order.total_amount,
        paid_amount=order.paid_amount,
        balance_amount=order.balance_amount,
        created_at=order.created_at,
        items=items
    )


@app.get("/orders/customer/{email}", response_model=List[OrderResponse])
async def get_customer_orders(email: str, db: Session = Depends(get_db)):
    """Get all orders for a specific customer."""
    orders = db.query(Order).filter(Order.customer_email == email).all()
    return orders


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.SERVICE_PORT)
