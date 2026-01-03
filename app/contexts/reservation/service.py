# app/contexts/reservation/service.py
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.core.errors import ValidationError, NotFoundError, ConflictError
from app.shared.services.event_publisher import publish_event_async

from app.contexts.seat_availability.repository import SeatLockRepository
from app.contexts.seat_availability.models import StatusEnum
from app.contexts.showtime.models import Showtime
from app.contexts.screen.models import Screen, SeatLayout

from .models import Reservation, ReservationStatus
from .schemas import ReservationCreate
from .repository import ReservationRepository
from .events import (
    reservation_created_event,
    reservation_cancelled_event,
    reservation_expired_event,
)


RESERVATION_DURATION = timedelta(minutes=10)


class ReservationService:
    """Service for Reservation business logic."""
    
    def __init__(self):
        self.repo = ReservationRepository()
        self.seat_repo = SeatLockRepository()

    async def create_reservation(
        self,
        db: Session,
        user_id: int,
        data: ReservationCreate,
    ) -> Reservation:
        """Create a new reservation."""
        # Basic validation
        if not data.seat_code:
            raise ValidationError("Seat code is required")

        # ===== VALIDATE SEAT EXISTS IN LAYOUT =====
        # Get showtime to find screen
        showtime = db.get(Showtime, data.showtime_id)
        if not showtime:
            raise NotFoundError("Showtime not found")
        
        # Get screen and layout
        screen = db.get(Screen, showtime.screen_id)
        if not screen:
            raise NotFoundError("Screen not found")
        
        layout = db.get(SeatLayout, screen.seat_layout_id)
        if not layout:
            raise NotFoundError("Seat layout not found")
        
        # Validate seat code exists in grid
        if layout.grid:
            # Parse seat code (e.g., "A-5" -> row "A", seat "5")
            try:
                row_part, seat_num = data.seat_code.split('-')
                seat_num = int(seat_num)
            except (ValueError, AttributeError):
                raise ValidationError(
                    f"Invalid seat code format: {data.seat_code}",
                    {"expected_format": "ROW-NUMBER (e.g., A-5)"}
                )
            
            # Check if row exists
            if row_part not in layout.grid:
                raise ValidationError(
                    f"Invalid row: {row_part}",
                    {"available_rows": list(layout.grid.keys())}
                )
            
            # Check if seat exists in row
            row_seats = layout.grid[row_part]
            if data.seat_code not in row_seats:
                raise ValidationError(
                    f"Seat {data.seat_code} does not exist in row {row_part}",
                    {"available_seats": [s for s in row_seats if s != "AISLE"]}
                )
        # If no grid, fall back to basic validation (rows x seats_per_row)
        else:
            try:
                row_part, seat_num = data.seat_code.split('-')
                seat_num = int(seat_num)
                
                # Basic bounds check
                if seat_num < 1 or seat_num > layout.seats_per_row:
                    raise ValidationError(
                        f"Seat number must be between 1 and {layout.seats_per_row}"
                    )
            except (ValueError, AttributeError):
                raise ValidationError("Invalid seat code format")
        # ===== END SEAT VALIDATION =====

        # ===== PRE-CHECK SEAT AVAILABILITY =====
        seat_lock = self.seat_repo.get_by_showtime_and_code(
            db, 
            data.showtime_id, 
            data.seat_code
        )
        
        # If seat exists and is not available, reject immediately
        if seat_lock:
            if seat_lock.status == StatusEnum.RESERVED:
                raise ValidationError(
                    "Seat is already reserved",
                    {"seat_code": data.seat_code}
                )
            if seat_lock.status == StatusEnum.LOCKED and seat_lock.locked_by_user_id != user_id:
                raise ValidationError(
                    "Seat is locked by another user",
                    {"seat_code": data.seat_code}
                )
        # ===== END PRE-CHECK =====

        # Expiration time aligned with seat lock duration
        now = datetime.now(timezone.utc)
        expires_at = now + RESERVATION_DURATION

        reservation = Reservation(
            user_id=user_id,
            showtime_id=data.showtime_id,
            seat_code=data.seat_code,
            status=ReservationStatus.ACTIVE,
            expires_at=expires_at,
        )

        reservation = self.repo.create(db, reservation)

        # Emit event
        event = reservation_created_event(
            reservation_id=reservation.id,
            user_id=user_id,
            showtime_id=data.showtime_id,
            seat_code=data.seat_code,
        )
        await publish_event_async(event["type"], event["payload"])

        return reservation

    async def cancel_reservation(
        self,
        db: Session,
        reservation_id: int,
        user_id: int = None,
        allow_admin_override: bool = False,
    ) -> Reservation:
        """Cancel a reservation."""
        reservation = self.repo.get_by_id(db, reservation_id)
        if reservation is None:
            raise NotFoundError("Reservation not found")

        # Check ownership (unless admin override)
        if user_id is not None and not allow_admin_override:
            if reservation.user_id != user_id:
                raise ConflictError("Cannot cancel another user's reservation")

        if reservation.status != ReservationStatus.ACTIVE:
            # Idempotent: if already terminal, just return
            return reservation

        reservation.status = ReservationStatus.CANCELLED
        reservation.expires_at = None

        reservation = self.repo.save(db, reservation)

        # Emit event
        event = reservation_cancelled_event(reservation.id)
        await publish_event_async(event["type"], event["payload"])

        return reservation

    async def expire_reservation(
        self,
        db: Session,
        reservation: Reservation,
    ) -> Reservation:
        """Expire a reservation (called by background worker)."""
        if reservation.status != ReservationStatus.ACTIVE:
            return reservation

        reservation.status = ReservationStatus.EXPIRED
        reservation.expires_at = None

        reservation = self.repo.save(db, reservation)

        # Emit event
        event = reservation_expired_event(reservation.id)
        await publish_event_async(event["type"], event["payload"])

        return reservation

    async def sweep_expired_reservations(self, db: Session) -> int:
        """Background task: expire all reservations past their expiration time."""
        now = datetime.now(timezone.utc)
        expired = self.repo.get_expired(db, now)

        for res in expired:
            await self.expire_reservation(db, reservation=res)

        return len(expired)
    
    # ===== READ OPERATIONS (sync) =====
    
    def get_reservation(self, db: Session, reservation_id: int) -> Reservation:
        """Get reservation by ID."""
        reservation = self.repo.get_by_id(db, reservation_id)
        if not reservation:
            raise NotFoundError("Reservation not found")
        return reservation
    
    def list_user_reservations(self, db: Session, user_id: int):
        """List all reservations for a user."""
        return self.repo.list_for_user(db, user_id)