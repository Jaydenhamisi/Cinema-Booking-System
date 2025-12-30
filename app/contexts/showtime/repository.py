# app/contexts/showtime/repository.py
from sqlalchemy.orm import Session
from sqlalchemy import select
from .models import Showtime


class ShowtimeRepository:
    """Repository for Showtime aggregate."""

    def get_by_id(self, db: Session, showtime_id: int):
        """Get showtime by ID."""
        return db.get(Showtime, showtime_id)

    def list_all(self, db: Session):
        """List all showtimes."""
        return db.scalars(select(Showtime)).all()

    def list_for_movie(self, db: Session, movie_id: int):
        """List all showtimes for a specific movie."""
        return db.scalars(
            select(Showtime).where(Showtime.movie_id == movie_id)
        ).all()

    def list_for_screen(self, db: Session, screen_id: int):
        """List all showtimes for a specific screen."""
        return db.scalars(
            select(Showtime).where(Showtime.screen_id == screen_id)
        ).all()

    def find_overlap(self, db: Session, screen_id: int, start_time, end_time, exclude_id: int = None):
        """Find overlapping showtimes for a screen."""
        stmt = select(Showtime).where(
            Showtime.screen_id == screen_id,
            Showtime.start_time < end_time,
            Showtime.end_time > start_time,
            Showtime.is_active == True,
        )

        if exclude_id:
            stmt = stmt.where(Showtime.id != exclude_id)

        return db.scalar(stmt)

    def create(self, db: Session, showtime: Showtime):
        """Create a new showtime."""
        db.add(showtime)
        db.commit()
        db.refresh(showtime)
        return showtime

    def save(self, db: Session, showtime: Showtime):
        """Update existing showtime."""
        db.add(showtime)
        db.commit()
        db.refresh(showtime)
        return showtime

    def delete(self, db: Session, showtime: Showtime):
        """Delete a showtime."""
        db.delete(showtime)
        db.commit()