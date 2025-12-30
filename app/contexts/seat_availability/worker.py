# app/contexts/seat_availability/worker.py

"""
SeatAvailability Expiration Worker
"""

from datetime import datetime, timezone
from app.core.database import SessionLocal
from .service import SeatAvailabilityService


def utcnow():
    """Return timezone-aware UTC datetime."""
    return datetime.now(timezone.utc)


async def run_expiration_sweep() -> int:
    """
    Perform one sweep of the expiration process.
    Returns the number of seat locks that were expired/unlocked.
    """
    seat_service = SeatAvailabilityService()
    
    db = SessionLocal()
    try:
        expired_count = await seat_service.expire_seats(db)
        return expired_count
    finally:
        db.close()