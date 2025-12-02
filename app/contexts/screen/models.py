# app/contexts/screen/models.py

from sqlalchemy import Column, Integer, String, ForeignKey, JSON
from sqlalchemy.orm import relationship

from app.core.database import Base


class Screen(Base):
    __tablename__ = "screens"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)

    capacity = Column(Integer, nullable=False)

    seat_layout_id = Column(
        Integer,
        ForeignKey("seat_layouts.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    # Relationship to the SeatLayout aggregate (same context)
    layout = relationship(
        "SeatLayout",
        back_populates="screens",
        lazy="selectin",
    )
    # IMPORTANT: no relationship to Showtime here.
    # ShowtimeContext will reference Screen, not the other way around.


class SeatLayout(Base):
    __tablename__ = "seat_layouts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)

    rows = Column(Integer, nullable=False)
    seats_per_row = Column(Integer, nullable=False)

    # Optional structural grid JSON (seat types, blocked seats, etc.)
    grid = Column(JSON, nullable=True)

    screens = relationship(
        "Screen",
        back_populates="layout",
        lazy="selectin",
    )



