from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.core.errors import ValidationError, NotFoundError, ConflictError
from app.shared.services.event_publisher import publish_event

from .models import Reservation, ReservationStatus
from .schemas import ReservationCreate
from .repository import ReservationRepository
from .events import (
    reservation_created_event,
    reservation_cancelled_event,
    reservation_expired_event,
)

repo = ReservationRepository()

RESERVATION_DURATION = timedelta(minutes=10)


def create_reservation(
    db: Session,
    *,
    user_id: int,
    data: ReservationCreate,
) -> Reservation:
    # Basic validation
    if not data.seat_code:
        raise ValidationError("Seat code is required")

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

    reservation = repo.create(db, reservation)

    event = reservation_created_event(
        reservation_id=reservation.id,
        user_id=user_id,
        showtime_id=data.showtime_id,
        seat_code=data.seat_code,
    )
    publish_event(event["type"], event["payload"])

    return reservation


def cancel_reservation(
    db: Session,
    *,
    reservation_id: int,
    user_id: int | None = None,
    allow_admin_override: bool = False,
) -> Reservation:
    reservation = repo.get_by_id(db, reservation_id)
    if reservation is None:
        raise NotFoundError("Reservation not found")

    # Optional: user ownership check (plug this in once auth is wired)
    if user_id is not None and not allow_admin_override:
        if reservation.user_id != user_id:
            raise ConflictError("Cannot cancel another user's reservation")

    if reservation.status != ReservationStatus.ACTIVE:
        # idempotent: if already terminal, do nothing
        return reservation

    reservation.status = ReservationStatus.CANCELLED
    reservation.expires_at = None

    reservation = repo.save(db, reservation)

    event = reservation_cancelled_event(reservation.id)
    publish_event(event["type"], event["payload"])

    return reservation


def expire_reservation(
    db: Session,
    *,
    reservation: Reservation,
) -> Reservation:
    if reservation.status != ReservationStatus.ACTIVE:
        return reservation

    reservation.status = ReservationStatus.EXPIRED
    reservation.expires_at = None

    reservation = repo.save(db, reservation)

    event = reservation_expired_event(reservation.id)
    publish_event(event["type"], event["payload"])

    return reservation


def sweep_expired_reservations(db: Session) -> int:
    now = datetime.now(timezone.utc)
    expired = repo.get_expired(db, now)

    for res in expired:
        expire_reservation(db, reservation=res)

    return len(expired)
