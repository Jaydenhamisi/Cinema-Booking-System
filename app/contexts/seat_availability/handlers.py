# app/contexts/seat_availability/handlers.py
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.core.event_bus import event_bus

from .service import SeatAvailabilityService

# Create service instance
seat_service = SeatAvailabilityService()


async def on_reservation_created(payload: dict):
    db = SessionLocal()
    try:
        showtime_id = payload.get("showtime_id")
        seat_code = payload.get("seat_code")
        user_id = payload.get("user_id")

        if not showtime_id or not seat_code or not user_id:
            return

        await seat_service.lock_seat(
            db,
            showtime_id=showtime_id,
            seat_code=seat_code,
            user_id=user_id,
        )
    finally:
        db.close()


async def on_reservation_cancelled(payload: dict):
    db = SessionLocal()
    try:
        showtime_id = payload.get("showtime_id")
        seat_code = payload.get("seat_code")

        if not showtime_id or not seat_code:
            return
        
        await seat_service.unlock_seat(
            db,
            showtime_id=showtime_id,
            seat_code=seat_code,
        )
    finally:
        db.close()


async def on_payment_succeeded(payload: dict):
    db = SessionLocal()
    try:
        showtime_id = payload.get("showtime_id")
        seat_code = payload.get("seat_code")

        if not showtime_id or not seat_code:
            return
        
        await seat_service.mark_reserved(
            db,
            showtime_id=showtime_id,
            seat_code=seat_code,
        )
    finally:
        db.close()


async def on_payment_failed(payload: dict):
    db = SessionLocal()
    try:
        showtime_id = payload.get("showtime_id")
        seat_code = payload.get("seat_code")

        if not showtime_id or not seat_code:
            return
        
        await seat_service.unlock_seat(
            db,
            showtime_id=showtime_id,
            seat_code=seat_code,
        )
    finally:
        db.close()


async def on_order_expired(payload: dict):
    db = SessionLocal()
    try:
        showtime_id = payload.get("showtime_id")
        seat_code = payload.get("seat_code")

        if not showtime_id or not seat_code:
            return
        
        await seat_service.unlock_seat(
            db,
            showtime_id=showtime_id,
            seat_code=seat_code,
        )
    finally:
        db.close()


async def on_showtime_cancelled(payload: dict):
    db = SessionLocal()
    try:
        showtime_id = payload.get("showtime_id")
        if not showtime_id:
            return
        
        from .repository import SeatLockRepository
        repo = SeatLockRepository()
        seats = repo.list_for_showtime(db, showtime_id)

        for seat in seats:
            await seat_service.unlock_seat(
                db,
                showtime_id=showtime_id,
                seat_code=seat.seat_code,
            )
    finally:
        db.close()


async def on_admin_force_unlock(payload: dict):
    db = SessionLocal()
    try:
        showtime_id = payload.get("showtime_id")
        seat_code = payload.get("seat_code")

        if not showtime_id or not seat_code:
            return
        
        await seat_service.unlock_seat(
            db,
            showtime_id=showtime_id,
            seat_code=seat_code,
        )
    finally:
        db.close()


# Event bus subscriptions
event_bus.subscribe("reservation.created", on_reservation_created)
event_bus.subscribe("reservation.cancelled", on_reservation_cancelled)
event_bus.subscribe("payment.succeeded", on_payment_succeeded)
event_bus.subscribe("payment.failed", on_payment_failed)
event_bus.subscribe("order.expired", on_order_expired)
event_bus.subscribe("showtime.cancelled", on_showtime_cancelled)
event_bus.subscribe("admin.force_unlock_seat", on_admin_force_unlock)