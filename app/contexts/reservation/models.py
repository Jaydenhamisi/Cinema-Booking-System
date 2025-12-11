from enum import Enum as PyEnum
from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Enum as SAEnum,
    ForeignKey,
    Index,
)
from sqlalchemy.orm import relationship

from app.core.database import Base


class ReservationStatus(str, PyEnum):
    ACTIVE = "active"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class Reservation(Base):
    __tablename__ = "reservations"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, nullable=False)
    showtime_id = Column(Integer, ForeignKey("showtimes.id"), nullable=False)

    
    seat_code = Column(String, nullable=False)
    status = Column(
        SAEnum(ReservationStatus, name="Reservation_status"),
        nullable=False,
        default=ReservationStatus.ACTIVE,
    )

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )
    expires_at = Column(DateTime(timezone=True), nullable=True)

    showtime = relationship("Showtime", back_populates="reservations")

    __table_args__ = (
        Index(
            "ix_reservations_showtime_seat",
            "showtime_id",
            "seat_code"
        ),
    )