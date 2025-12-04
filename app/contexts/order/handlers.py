# app/contexts/order/handlers.py

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.core.event_bus import event_bus

from .service import (
    create_order_from_event,
    complete_order_from_event,
    cancel_order_from_event,
    expire_order_from_event,
) 

from .repository import OrderRepository

repo = OrderRepository()

async def on_reservation_created(payload: dict):
    db = SessionLocal()
    try:
        user_id = payload.get("user_id")
        reservation_id = payload.get("reservation_id")
        showtime_id = payload.get("showtime_id")
        seat_code = payload.get("seat_code")

        if not user_id or not seat_code or not reservation_id or not showtime_id:
            return
        
        create_order_from_event(
            db,
            user_id=user_id,
            reservation_id=reservation_id,
            showtime_id=showtime_id,
            seat_code=seat_code,
        )
    finally:
        db.close()


async def on_reservation_cancelled(payload: dict):
    reservation_id = payload.get("reservation_id")

    if not reservation_id:
            return
    
    db = SessionLocal()
    try:
        order = repo.get_order_by_reservation_id(
            db,
            reservation_id=reservation_id,
        )
        if order:
            cancel_order_from_event(db, order_id=order.id)
    finally:
        db.close()


async def on_reservation_expired(payload: dict):
    reservation_id = payload.get("reservation_id")

    if not reservation_id:
            return
    
    db = SessionLocal()
    try:
        order = repo.get_order_by_reservation_id(
            db,
            reservation_id=reservation_id,
        )
        if order:
            expire_order_from_event(db, order_id=order.id)
    finally:
        db.close()


event_bus.subscribe("reservation.created", on_reservation_created)
event_bus.subscribe("reservation.cancelled", on_reservation_cancelled)
event_bus.subscribe("reservation.expired", on_reservation_expired)