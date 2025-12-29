# app/contexts/showtime/models.py

from enum import Enum as PyEnum
from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    DateTime,
    Boolean,
    Enum as SAEnum,
)
from sqlalchemy.orm import relationship

from app.core.base import Base 


class FormatEnum(str, PyEnum):
    TWO_D = "2D"
    THREE_D = "3D"
    IMAX_2D = "IMAX_2D"
    IMAX_3D = "IMAX_3D"
    DOLBY = "DOLBY"


class Showtime(Base):
    __tablename__ = "showtimes"

    id = Column(Integer, primary_key=True, index=True)

    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)

    is_active = Column(Boolean, nullable=False, default=True)

    format = Column(
        SAEnum(FormatEnum, name="showtime_format"),
        nullable=False,
    )

    movie_id = Column(
        Integer,
        ForeignKey("movies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    screen_id = Column(
        Integer,
        ForeignKey("screens.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    movie = relationship("Movie", lazy="selectin")
    screen = relationship("Screen", lazy="selectin")

    

