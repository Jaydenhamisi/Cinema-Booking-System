# app/contexts/payment/schemas.py

from typing import Optional
from datetime import datetime

from pydantic import BaseModel

from .models import PaymentStatus

class PaymentAttemptRead(BaseModel):
    id: int
    order_id: int
    amount_attempted: float
    final_amount: float
    status: PaymentStatus | str 
    failure_reason: Optional[str]
    provider_payment_id: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}

