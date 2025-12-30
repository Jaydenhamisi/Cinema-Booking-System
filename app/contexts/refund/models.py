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

from app.core.base import Base 


class RefundStatus(str, PyEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMPLETED = "completed"


class RefundRequest(Base):
    __tablename__ = "refund_requests"

    id = Column(Integer, primary_key=True, index=True)

    reservation_id = Column(Integer, ForeignKey("reservations.id"), nullable=False)
    payment_attempt_id = Column(Integer, ForeignKey("payment_attempts.id"), nullable=False)

    amount = Column(Float, nullable=False)
    reason = Column(String, nullable=False)
    
    status = Column(
        SAEnum(RefundStatus, name="refund_request_status"),
        nullable=False,
        default=RefundStatus.PENDING
    )
    
    # Fields for rejection and completion
    rejection_reason = Column(String, nullable=True)
    provider_refund_id = Column(String, nullable=True)
    
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )