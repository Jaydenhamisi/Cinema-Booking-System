# app/contexts/order/schemas.py

from typing import Dict
from datetime import datetime
from pydantic import BaseModel


class OrderRead(BaseModel):
    id: int
    user_id: int
    reservation_id: int
    pricing_snapshot: Dict
    final_amount: int
    is_completed: bool
    created_at: datetime

    model_config = {"from_attributes": True}



