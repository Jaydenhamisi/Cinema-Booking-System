from enum import Enum as PyEnum
from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    Float,
    Integer,
    String,
    DateTime,
    Enum as SAEnum,
    ForeignKey
)
from sqlalchemy.orm import relationship

from app.core.database import Base


class RefundStatus(str, PyEnum):
    ISSUED = "issued"
    FAILED = "failed"


class Refund(Base):
    __tablename__ = "refunds"

    id = Column(Integer, primary_key=True, index=True)

    reservation_id = Column(Integer, ForeignKey("reservations.id"), nullable=False)

    payment_attempt_id = Column(Integer, ForeignKey("payment_attempts.id"), nullable=False)

    amount = Column(Float, nullable=False)

    reason = Column(String, nullable=False)
    
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )

    status = Column(
        SAEnum(RefundStatus, name="refund_status"),
        nullable=False,
        default=RefundStatus.ISSUED
    )