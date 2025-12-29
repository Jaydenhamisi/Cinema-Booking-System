from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Boolean,
    JSON
)

from app.core.base import Base 


class PriceModifier(Base):
    __tablename__ = "price_modifiers"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, unique=True, nullable=False)

    modifier_type = Column(String, nullable=False)

    amount = Column(Float, nullable=False)

    is_active = Column(Boolean, nullable=False, default=True)

    applies_to = Column(JSON, nullable=True)