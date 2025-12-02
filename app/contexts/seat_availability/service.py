# app/contexts/seat_availability/service.py

from datetime import timedelta
from sqlalchemy.orm import Session

from app.core.utils import utcnow
from app.core.errors import NotFoundError, ValidationError
from app.shared.services.event_publisher import publish_event

from .models import StatusEnum
from .repository import SeatLockRepository


LOCK_DURATION = timedelta(minutes=10)

seat_repo = SeatLockRepository()


class SeatAvailabilityService:

    @staticmethod
    def lock_seat(
        db: Session, *, showtime_id: int, seat_code: str, user_id: int
    ):
        seat = seat_repo.get_by_showtime_and_code(db, showtime_id, seat_code)
        if not seat:
            raise NotFoundError("Seat does not exist", {"seat_code": seat_code})

        # Cannot lock reserved seats
        if seat.status == StatusEnum.RESERVED:
            raise ValidationError(
                "Seat is already reserved", {"seat_code": seat_code}
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

        publish_event(
            "seat.locked",
            {
                "showtime_id": showtime_id,
                "seat_code": seat_code,
                "user_id": user_id,
                "expires_at": seat.lock_expires_at.isoformat(),
            },
        )

        return seat

    @staticmethod
    def unlock_seat(
        db: Session, *, showtime_id: int, seat_code: str
    ):
        seat = seat_repo.get_by_showtime_and_code(db, showtime_id, seat_code)
        if not seat:
            raise NotFoundError("Seat not found", {"seat_code": seat_code})

        # Transition → AVAILABLE
        seat.status = StatusEnum.AVAILABLE
        seat.locked_by_user_id = None
        seat.lock_expires_at = None

        db.commit()
        db.refresh(seat)

        publish_event(
            "seat.unlocked",
            {
                "showtime_id": showtime_id,
                "seat_code": seat_code,
            },
        )

        return seat

    @staticmethod
    def mark_reserved(
        db: Session, *, showtime_id: int, seat_code: str
    ):
        seat = seat_repo.get_by_showtime_and_code(db, showtime_id, seat_code)
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

        publish_event(
            "seat.reserved",
            {
                "showtime_id": showtime_id,
                "seat_code": seat_code,
            },
        )

        return seat

    @staticmethod
    def expire_seats(db: Session) -> int:
        now = utcnow()

        expired_seats = seat_repo.get_expired(db, now)

        for seat in expired_seats:
            seat.status = StatusEnum.AVAILABLE
            seat.locked_by_user_id = None
            seat.lock_expires_at = None

            publish_event(
                "seat.expired",
                {
                    "showtime_id": seat.showtime_id,
                    "seat_code": seat.seat_code,
                },
            )

        db.commit()
        return len(expired_seats)

    @staticmethod
    def get_availability_grid(db: Session, showtime_id: int):
        seats = seat_repo.list_for_showtime(db, showtime_id)

        return [
            {
                "seat_code": seat.seat_code,
                "status": seat.status.value,
            }
            for seat in seats
        ]

