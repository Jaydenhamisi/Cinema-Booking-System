from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from .models import ReservationStatus



class ReservationBase(BaseModel):
    showtime_id: int
    seat_code: str


class ReservationCreate(ReservationBase):
    pass 


class ReservationUpdate(BaseModel):
    status: Optional[ReservationStatus] = None


class ReservationRead(ReservationBase):
    id: int
    user_id: int
    status: ReservationStatus
    created_at: datetime
    expires_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
    