# app/contexts/seat_availability/worker.py

"""
SeatAvailability Expiration Worker

This worker is responsible for:
- finding all expired seat locks
- unlocking them
- emitting `seat.expired` events via the service layer

It should be executed periodically (e.g. every 30–60 seconds)
by a scheduler, background task, or FastAPI startup task.
"""

from datetime import datetime, timezone
from app.core.database import SessionLocal
from .service import SeatAvailabilityService

seat_service = SeatAvailabilityService()


def utcnow():
    """Return timezone-aware UTC datetime."""
    return datetime.now(timezone.utc)


def run_expiration_sweep() -> int:
    """
    Perform one sweep of the expiration process.

    Returns:
        int: Number of seat locks that were expired/unlocked.
    """
    db = SessionLocal()
    try:
        # Service handles:
        # - querying expired locks
        # - unlocking seats
        # - emitting `seat.expired` events
        expired_count = seat_service.expire_seats(db)
        return expired_count
    finally:
        db.close()

