# app/contexts/showtime/schemas.py

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field

from .models import FormatEnum


class ShowtimeBase(BaseModel):
    start_time: datetime
    end_time: datetime
    format: FormatEnum
    movie_id: int = Field(gt=0)
    screen_id: int = Field(gt=0)


class ShowtimeCreate(ShowtimeBase):
    pass


class ShowtimeUpdate(BaseModel):
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    format: Optional[FormatEnum] = None
    movie_id: Optional[int] = Field(default=None, gt=0)
    screen_id: Optional[int] = Field(default=None, gt=0)
    is_active: Optional[bool] = None


class ShowtimeRead(ShowtimeBase):
    id: int
    is_active: bool

    model_config = {"from_attributes": True}


    


