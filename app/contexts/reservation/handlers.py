# app/contexts/reservation/handlers.py
from app.core.database import SessionLocal
from app.core.event_bus import event_bus

from .models import ReservationStatus
from .service import ReservationService

reservation_service = ReservationService()


async def on_seat_expired(payload: dict):
    showtime_id = payload.get("showtime_id")
    seat_code = payload.get("seat_code")

    if not showtime_id or not seat_code:
        return

    db = SessionLocal()
    try:
        # Get reservation directly from repo (handler doesn't go through service for this)
        from .repository import ReservationRepository
        repo = ReservationRepository()
        
        reservation = repo.get_active_by_showtime_and_seat(
            db,
            showtime_id=showtime_id,
            seat_code=seat_code,
        )
        if reservation:
            await reservation_service.expire_reservation(db, reservation=reservation)
    finally:
        db.close()


async def on_showtime_cancelled(payload: dict):
    showtime_id = payload.get("showtime_id")
    if not showtime_id:
        return

    db = SessionLocal()
    try:
        from .repository import ReservationRepository
        repo = ReservationRepository()
        
        reservations = repo.list_active_for_showtime(db, showtime_id)
        for res in reservations:
            await reservation_service.cancel_reservation(
                db,
                reservation_id=res.id,
                allow_admin_override=True,
            )
    finally:
        db.close()


async def on_admin_force_cancel_reservation(payload: dict):
    reservation_id = payload.get("reservation_id")
    if not reservation_id:
        return

    db = SessionLocal()
    try:
        await reservation_service.cancel_reservation(
            db,
            reservation_id=reservation_id,
            allow_admin_override=True,
        )
    finally:
        db.close()


event_bus.subscribe("seat.expired", on_seat_expired)
event_bus.subscribe("showtime.cancelled", on_showtime_cancelled)
event_bus.subscribe("admin.force_cancel_reservation", on_admin_force_cancel_reservation)