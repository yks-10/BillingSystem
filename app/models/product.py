from sqlalchemy import Column, Integer, String, Float
from app.core.database import Base
from sqlalchemy.sql import func
from sqlalchemy import DateTime

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    tax_percentage = Column(Float, nullable=False)
    available_stock = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
