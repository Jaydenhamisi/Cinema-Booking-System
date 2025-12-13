from datetime import datetime
from pydantic import BaseModel

from .models import RefundStatus


class RefundRead(BaseModel):
    id: int
    reservation_id: int
    payment_attempt_id: int
    amount: float
    reason: str
    status: RefundStatus
    created_at: datetime

    model_config = {"from_attributes": True}