from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    customer_email = Column(String, nullable=False, index=True)
    total_without_tax = Column(Float, nullable=False)
    total_tax = Column(Float, nullable=False)
    total_amount = Column(Float, nullable=False)
    paid_amount = Column(Float, nullable=False)
    balance_amount = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True),
                        server_default=func.now())
    # relationship
    items = relationship("OrderItem", back_populates="order")
