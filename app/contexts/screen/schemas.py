# app/contexts/screen/schemas.py

from typing import Optional, Dict
from pydantic import BaseModel, Field


# ---------------------------------------------------------------
# Screen Schemas
# ---------------------------------------------------------------


class ScreenBase(BaseModel):
    name: str
    capacity: int = Field(gt=0)
    seat_layout_id: int = Field(gt=0)


class ScreenCreate(ScreenBase):
    pass


class ScreenUpdate(BaseModel):
    name: Optional[str] = None
    capacity: Optional[int] = Field(default=None, gt=0)
    seat_layout_id: Optional[int] = Field(default=None, gt=0)


class ScreenRead(ScreenBase):
    id: int

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------
# Layout Schemas
# ---------------------------------------------------------------


class SeatLayoutBase(BaseModel):
    name: str
    rows: int = Field(gt=0)
    seats_per_row: int = Field(gt=0)
    grid: Optional[Dict] = None


class SeatLayoutCreate(SeatLayoutBase):
    pass


class SeatLayoutUpdate(BaseModel):
    name: Optional[str] = None
    rows: Optional[int] = Field(default=None, gt=0)
    seats_per_row: Optional[int] = Field(default=None, gt=0)
    grid: Optional[Dict] = None


class SeatLayoutRead(SeatLayoutBase):
    id: int

    model_config = {"from_attributes": True}
