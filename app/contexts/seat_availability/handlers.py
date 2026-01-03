# app/contexts/seat_availability/handlers.py

from app.core.database import SessionLocal
from app.core.event_bus import event_bus

from .service import SeatAvailabilityService

seat_service = SeatAvailabilityService()


async def on_reservation_created(payload: dict):
    """Lock seat when reservation is created"""
    showtime_id = payload.get("showtime_id")
    seat_code = payload.get("seat_code")
    user_id = payload.get("user_id")
    
    if not all([showtime_id, seat_code, user_id]):
        return
    
    db = SessionLocal()
    try:
        await seat_service.lock_seat(db, showtime_id, seat_code, user_id)
    finally:
        db.close()


async def on_order_completed(payload: dict):
    """Mark seat as RESERVED when order is completed (payment succeeded)"""
    # Need to get seat info from order
    from app.contexts.order.repository import OrderRepository
    from app.contexts.reservation.repository import ReservationRepository
    
    order_id = payload.get("order_id")
    if not order_id:
        return
    
    db = SessionLocal()
    try:
        # Get order
        order_repo = OrderRepository()
        order = order_repo.get_by_id(db, order_id)
        if not order:
            return
        
        # Get reservation to find seat info
        reservation_repo = ReservationRepository()
        reservation = reservation_repo.get_by_id(db, order.reservation_id)
        if not reservation:
            return
        
        # Mark seat as reserved
        await seat_service.mark_reserved(
            db,
            showtime_id=reservation.showtime_id,
            seat_code=reservation.seat_code
        )
    finally:
        db.close()


async def on_reservation_cancelled(payload: dict):
    """Unlock seat when reservation is cancelled"""
    # This should get showtime/seat from the event payload
    # For now, we'll need to look up the reservation
    reservation_id = payload.get("reservation_id")
    if not reservation_id:
        return
    
    from app.contexts.reservation.repository import ReservationRepository
    
    db = SessionLocal()
    try:
        reservation_repo = ReservationRepository()
        reservation = reservation_repo.get_by_id(db, reservation_id)
        if not reservation:
            return
        
        await seat_service.unlock_seat(
            db,
            showtime_id=reservation.showtime_id,
            seat_code=reservation.seat_code
        )
    finally:
        db.close()


async def on_reservation_expired(payload: dict):
    """Unlock seat when reservation expires"""
    reservation_id = payload.get("reservation_id")
    if not reservation_id:
        return
    
    from app.contexts.reservation.repository import ReservationRepository
    
    db = SessionLocal()
    try:
        reservation_repo = ReservationRepository()
        reservation = reservation_repo.get_by_id(db, reservation_id)
        if not reservation:
            return
        
        await seat_service.unlock_seat(
            db,
            showtime_id=reservation.showtime_id,
            seat_code=reservation.seat_code
        )
    finally:
        db.close()


# Subscribe to events
event_bus.subscribe("reservation.created", on_reservation_created)
event_bus.subscribe("order.completed", on_order_completed)
event_bus.subscribe("reservation.cancelled", on_reservation_cancelled)
event_bus.subscribe("reservation.expired", on_reservation_expired)