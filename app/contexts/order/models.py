from sqlalchemy import (
    Column,
    Integer,
    DateTime,
    ForeignKey,
    JSON,
    Boolean,
    func,
)
from sqlalchemy.orm import relationship

from app.core.base import Base 


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, nullable=False)

    pricing_snapshot = Column(JSON, nullable=False)

    final_amount = Column(Integer, nullable=False)

    is_completed = Column(Boolean, nullable=False, default=False)

    reservation_id = Column(
        Integer, 
        ForeignKey("reservations.id"), 
        nullable=False
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    reservation = relationship("Reservation")
