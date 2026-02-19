"""Denomination Service database models."""

from sqlalchemy import Column, Integer
from .database import Base


class Denomination(Base):
    """Denomination model."""
    __tablename__ = "denominations"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    value = Column(Integer, unique=True, index=True, nullable=False)
    available_count = Column(Integer, nullable=False, default=0)
