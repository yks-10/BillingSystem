from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.product import Product
from app.schemas.order import OrderResponse, OrderItemResponse

router = APIRouter(
    prefix="/orders",
    tags=["Orders"]
)


@router.get("/customer/{customer_email}", response_model=List[OrderResponse])
async def get_customer_orders(
    customer_email: str,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get all orders for a specific customer by email.
    
    Args:
        customer_email: Customer email address
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session
        
    Returns:
        List of orders with all details including items
    """
    orders = (
        db.query(Order)
        .filter(Order.customer_email == customer_email)
        .order_by(Order.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    
    # Enrich orders with item details including product names
    result = []
    for order in orders:
        order_items = []
        for item in order.items:
            product = db.query(Product).filter(Product.id == item.product_id).first()
            order_item_dict = {
                "product_id": item.product_id,
                "product_name": product.name if product else "Unknown",
                "quantity": item.quantity,
                "unit_price": item.unit_price,
                "tax_amount": item.tax_amount,
                "total_price": item.total_price
            }
            order_items.append(order_item_dict)
        
        order_dict = {
            "id": order.id,
            "customer_email": order.customer_email,
            "total_without_tax": order.total_without_tax,
            "total_tax": order.total_tax,
            "total_amount": order.total_amount,
            "paid_amount": order.paid_amount,
            "balance_amount": order.balance_amount,
            "created_at": order.created_at,
            "items": order_items
        }
        result.append(order_dict)
    
    return result


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order_details(
    order_id: int,
    db: Session = Depends(get_db)
):
    """
    Get details of a specific order including all items.
    
    Args:
        order_id: Order ID
        db: Database session
        
    Returns:
        Order details with all items
        
    Raises:
        HTTPException: If order not found
    """
    order = db.query(Order).filter(Order.id == order_id).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with ID {order_id} not found"
        )
    
    # Enrich order items with product names
    order_items = []
    for item in order.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        order_item_dict = {
            "product_id": item.product_id,
            "product_name": product.name if product else "Unknown",
            "quantity": item.quantity,
            "unit_price": item.unit_price,
            "tax_amount": item.tax_amount,
            "total_price": item.total_price
        }
        order_items.append(order_item_dict)
    
    order_dict = {
        "id": order.id,
        "customer_email": order.customer_email,
        "total_without_tax": order.total_without_tax,
        "total_tax": order.total_tax,
        "total_amount": order.total_amount,
        "paid_amount": order.paid_amount,
        "balance_amount": order.balance_amount,
        "created_at": order.created_at,
        "items": order_items
    }
    
    return order_dict
