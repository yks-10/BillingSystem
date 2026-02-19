"""Order Service database models."""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base


class Order(Base):
    """Order model."""
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    customer_email = Column(String, index=True, nullable=False)
    total_without_tax = Column(Float, nullable=False)
    total_tax = Column(Float, nullable=False)
    total_amount = Column(Float, nullable=False)
    paid_amount = Column(Float, nullable=False)
    balance_amount = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationship
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")


class OrderItem(Base):
    """Order item model."""
    __tablename__ = "order_items"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(String, nullable=False)  # Store product_id as string (not FK to product service)
    product_name = Column(String, nullable=False)  # Denormalize for independence
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    tax_amount = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)
    
    # Relationship
    order = relationship("Order", back_populates="items")
