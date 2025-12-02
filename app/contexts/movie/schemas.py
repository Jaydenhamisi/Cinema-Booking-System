# app/contexts/movie/schemas.py

from typing import Optional
from datetime import date
from pydantic import BaseModel, Field, HttpUrl

from .models import AgeRatingEnum


class MovieBase(BaseModel):
    title: str
    description: Optional[str] = None
    duration_minutes: int
    release_date: Optional[date] = None
    age_rating: AgeRatingEnum
    poster_url: Optional[HttpUrl] = None
    trailer_url: Optional[HttpUrl] = None


class MovieCreate(MovieBase):
    pass


class MovieUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    duration_minutes: Optional[int] = None
    release_date: Optional[date] = None
    age_rating: Optional[AgeRatingEnum] = None
    poster_url: Optional[HttpUrl] = None
    trailer_url: Optional[HttpUrl] = None
    is_active: Optional[bool] = None


class MovieRead(MovieBase):
    id: int
    is_active: bool

    model_config = {"from_attributes": True}

