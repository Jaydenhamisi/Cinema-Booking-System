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

class PaymentStatus(str, PyEnum):
    PENDING = "pending"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class PaymentAttempt(Base):
    __tablename__ = "payment_attempts"

    id = Column(Integer, primary_key=True, index=True)

    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)

    amount_attempted = Column(Float, nullable=False)

    status = Column(
        SAEnum(PaymentStatus, name="Payment_status"),
        nullable=False,
        default=PaymentStatus.PENDING
    )

    final_amount = Column(Float, nullable=False)

    failure_reason = Column(String, nullable=True)

    provider_payment_id = Column(String, nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )

    order = relationship("Order", back_populates="payment_attempts")