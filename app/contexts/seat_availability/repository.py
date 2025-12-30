# app/contexts/seat_availability/repository.py
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import select, and_

from .models import SeatLock, StatusEnum


class SeatLockRepository:
    """Repository for SeatLock aggregate."""

    def get_by_id(self, db: Session, seat_lock_id: int):
        """Get seat lock by ID."""
        return db.get(SeatLock, seat_lock_id)

    def get_by_showtime_and_code(self, db: Session, showtime_id: int, seat_code: str):
        """Get seat lock for a specific seat at a showtime."""
        return (
            db.query(SeatLock)
            .filter_by(showtime_id=showtime_id, seat_code=seat_code)
            .first()
        )

    def list_for_showtime(self, db: Session, showtime_id: int):
        """List all seat locks for a showtime."""
        return db.query(SeatLock).filter_by(showtime_id=showtime_id).all()

    def get_expired(self, db: Session, now: datetime):
        """Get all expired seat locks that need cleanup."""
        return (
            db.query(SeatLock)
            .filter(
                and_(
                    SeatLock.status == StatusEnum.LOCKED,
                    SeatLock.lock_expires_at != None,
                    SeatLock.lock_expires_at < now
                )
            )
            .all()
        )

    def create(self, db: Session, seat_lock: SeatLock):
        """Create a new seat lock."""
        db.add(seat_lock)
        db.commit()
        db.refresh(seat_lock)
        return seat_lock

    def save(self, db: Session, seat_lock: SeatLock):
        """Update existing seat lock."""
        db.add(seat_lock)
        db.commit()
        db.refresh(seat_lock)
        return seat_lock

    def delete(self, db: Session, seat_lock: SeatLock):
        """Delete a seat lock."""
        db.delete(seat_lock)
        db.commit()