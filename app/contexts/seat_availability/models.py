# app/context/seat_availability/models.py

from enum import Enum as PyEnum
from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    String,
    DateTime,
    Index,
    UniqueConstraint,
    Enum as SAEnum
)
from app.core.database import Base


class StatusEnum(str, PyEnum):
    AVAILABLE = "available"
    LOCKED = "locked"
    RESERVED = "reserved"


class SeatLock(Base):
    __tablename__ = "seat_locks"

    __table_args__ = (
        UniqueConstraint("showtime_id", "seat_code", name="uq_showtime_seat"),
        Index("idx_seatlock_showtime", "showtime_id"),
        Index("idx_seatlock_lock_expires", "lock_expires_at"),
    )

    id = Column(Integer, primary_key=True, index=True)

    seat_code = Column(String(10), nullable=False, index=True)

    showtime_id = Column(
        Integer,
        ForeignKey("showtimes.id"),
        nullable=False,
    )

    status = Column(SAEnum(StatusEnum), default=StatusEnum.AVAILABLE, index=True)

    locked_by_user_id = Column(Integer, nullable=True)

    lock_expires_at = Column(DateTime(timezone=True), nullable=True)



    

