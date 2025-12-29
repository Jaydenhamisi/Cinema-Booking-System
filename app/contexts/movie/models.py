from enum import Enum as PyEnum
from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    Boolean,
    Enum as SAEnum,
    Index,
    CheckConstraint,
)
from sqlalchemy.orm import relationship

from app.core.base import Base 


class AgeRatingEnum(str, PyEnum):
    G = "G"
    PG = "PG"
    PG_13 = "PG-13"
    R = "R"
    NC_17 = "NC-17"


class Movie(Base):
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(String, nullable=True)

    duration_minutes = Column(Integer, nullable=False)
    release_date = Column(Date, nullable=True)

    poster_url = Column(String(500), nullable=True)
    trailer_url = Column(String(500), nullable=True)

    is_active = Column(Boolean, nullable=False, default=True)

    age_rating = Column(
        SAEnum(AgeRatingEnum, name="movie_age_rating"),
        nullable=False,
    )

    __table_args__ = (
        Index("ix_movies_release_date", "release_date"),
        CheckConstraint("duration_minutes > 0", name="ck_duration_positive"),
    )

    showtimes = relationship("Showtime")





