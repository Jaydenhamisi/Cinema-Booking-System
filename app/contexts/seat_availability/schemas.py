# app/contexts/seat_availability/schemas.py

from typing import List
from datetime import datetime
from pydantic import BaseModel

from enum import Enum as PyEnum


class SeatStatus(str, PyEnum):
    AVAILABLE = "available"
    LOCKED = "locked"
    RESERVED = "reserved"


class SeatLockBase(BaseModel):
    seat_code: str
    showtime_id: int


class SeatLockCreate(SeatLockBase):
    pass


class SeatLockResponse(SeatLockBase):
    id: int
    status: SeatStatus
    locked_by_user_id: int | None = None
    lock_expires_at: datetime | None = None


class SeatAvailabilityGridItem(BaseModel):
    seat_code: str
    status: SeatStatus


class SeatAvailabilityGridResponse(BaseModel):
    showtime_id: int
    seats: List[SeatAvailabilityGridItem]