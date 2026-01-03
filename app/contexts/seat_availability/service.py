# app/contexts/seat_availability/service.py
from datetime import timedelta
from sqlalchemy.orm import Session

from app.core.utils import utcnow
from app.core.errors import NotFoundError, ValidationError
from app.shared.services.event_publisher import publish_event_async

from .models import SeatLock, StatusEnum
from .repository import SeatLockRepository


LOCK_DURATION = timedelta(minutes=10)


class SeatAvailabilityService:
    """Service for SeatAvailability business logic."""
    
    def __init__(self):
        self.repo = SeatLockRepository()

    async def lock_seat(
        self, 
        db: Session, 
        showtime_id: int, 
        seat_code: str, 
        user_id: int
    ):
        """Lock a seat for a user."""
        seat = self.repo.get_by_showtime_and_code(db, showtime_id, seat_code)
        
        # CREATE SEAT ON-DEMAND IF IT DOESN'T EXIST
        if not seat:
            seat = SeatLock(
                showtime_id=showtime_id,
                seat_code=seat_code,
                status=StatusEnum.AVAILABLE,
                locked_by_user_id=None,
                lock_expires_at=None,
            )
            db.add(seat)
            db.flush()  # Get the ID without committing

        # Cannot lock reserved seats
        if seat.status == StatusEnum.RESERVED:
            raise ValidationError(
                "Seat is already reserved", 
                {"seat_code": seat_code}
            )

        # If locked by someone else → cannot re-lock
        if seat.status == StatusEnum.LOCKED and seat.locked_by_user_id != user_id:
            raise ValidationError(
                "Seat locked by another user",
                {"locked_by": seat.locked_by_user_id, "attempt_user": user_id},
            )

        # Transition to LOCKED
        seat.status = StatusEnum.LOCKED
        seat.locked_by_user_id = user_id
        seat.lock_expires_at = utcnow() + LOCK_DURATION

        db.commit()
        db.refresh(seat)

        await publish_event_async(
            "seat.locked",
            {
                "showtime_id": showtime_id,
                "seat_code": seat_code,
                "user_id": user_id,
                "expires_at": seat.lock_expires_at.isoformat(),
            },
        )

        return seat

    async def unlock_seat(
        self, 
        db: Session, 
        showtime_id: int, 
        seat_code: str
    ):
        """Unlock a seat (make it available again)."""
        seat = self.repo.get_by_showtime_and_code(db, showtime_id, seat_code)
        if not seat:
            raise NotFoundError("Seat not found", {"seat_code": seat_code})

        # Transition → AVAILABLE
        seat.status = StatusEnum.AVAILABLE
        seat.locked_by_user_id = None
        seat.lock_expires_at = None

        db.commit()
        db.refresh(seat)

        await publish_event_async(
            "seat.unlocked",
            {
                "showtime_id": showtime_id,
                "seat_code": seat_code,
            },
        )

        return seat

    async def mark_reserved(
        self, 
        db: Session, 
        showtime_id: int, 
        seat_code: str
    ):
        """Mark a seat as reserved (after payment success)."""
        seat = self.repo.get_by_showtime_and_code(db, showtime_id, seat_code)
        if not seat:
            raise NotFoundError("Seat not found", {"seat_code": seat_code})

        # Must be LOCKED before becoming RESERVED
        if seat.status != StatusEnum.LOCKED:
            raise ValidationError(
                "Seat must be locked before reservation",
                {"current_status": seat.status.value},
            )

        seat.status = StatusEnum.RESERVED
        seat.locked_by_user_id = None
        seat.lock_expires_at = None

        db.commit()
        db.refresh(seat)

        await publish_event_async(
            "seat.reserved",
            {
                "showtime_id": showtime_id,
                "seat_code": seat_code,
            },
        )

        return seat

    async def expire_seats(self, db: Session) -> int:
        """Background task: expire all locked seats past their expiration time."""
        now = utcnow()

        expired_seats = self.repo.get_expired(db, now)

        for seat in expired_seats:
            seat.status = StatusEnum.AVAILABLE
            seat.locked_by_user_id = None
            seat.lock_expires_at = None

            await publish_event_async(
                "seat.expired",
                {
                    "showtime_id": seat.showtime_id,
                    "seat_code": seat.seat_code,
                },
            )

        db.commit()
        return len(expired_seats)

    def get_availability_grid(self, db: Session, showtime_id: int):
        """Get seat availability grid for a showtime - returns ALL seats from layout"""
        from app.contexts.showtime.models import Showtime
        from app.contexts.screen.models import Screen, SeatLayout
        
        # Get showtime to find screen
        showtime = db.get(Showtime, showtime_id)
        if not showtime:
            raise NotFoundError("Showtime not found")
        
        # Get screen and layout
        screen = db.get(Screen, showtime.screen_id)
        if not screen:
            raise NotFoundError("Screen not found")
        
        layout = db.get(SeatLayout, screen.seat_layout_id)
        if not layout:
            raise NotFoundError("Layout not found")
        
        # Get all existing seat locks for this showtime
        seat_locks = self.repo.list_for_showtime(db, showtime_id)
        seat_lock_map = {lock.seat_code: lock for lock in seat_locks}
        
        # Generate full grid from layout
        all_seats = []
        
        if layout.grid:
            # Use the grid to get all seats
            for row_name, row_seats in layout.grid.items():
                for seat_code in row_seats:
                    # Skip aisles
                    if seat_code == "AISLE":
                        continue
                    
                    # Check if this seat has a lock
                    if seat_code in seat_lock_map:
                        lock = seat_lock_map[seat_code]
                        all_seats.append({
                            "seat_code": seat_code,
                            "status": lock.status.value,
                        })
                    else:
                        # Seat exists in layout but not locked/reserved
                        all_seats.append({
                            "seat_code": seat_code,
                            "status": "available",
                        })
        else:
            # Fallback: generate from rows x seats_per_row
            row_letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            for row_idx in range(layout.rows):
                row = row_letters[row_idx]
                for seat_num in range(1, layout.seats_per_row + 1):
                    seat_code = f"{row}-{seat_num}"
                    
                    if seat_code in seat_lock_map:
                        lock = seat_lock_map[seat_code]
                        all_seats.append({
                            "seat_code": seat_code,
                            "status": lock.status.value,
                        })
                    else:
                        all_seats.append({
                            "seat_code": seat_code,
                            "status": "available",
                        })
        
        return all_seats