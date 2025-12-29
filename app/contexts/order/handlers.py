# app/contexts/order/handlers.py

import logging
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

logger = logging.getLogger(__name__)
repo = OrderRepository()


async def on_reservation_created(payload: dict):
    logger.info(f"🎫 Order handler received reservation.created: {payload}")
    db = SessionLocal()
    try:
        user_id = payload.get("user_id")
        reservation_id = payload.get("reservation_id")
        showtime_id = payload.get("showtime_id")
        seat_code = payload.get("seat_code")

        if not user_id or not seat_code or not reservation_id or not showtime_id:
            logger.error(f"Missing required fields in payload: {payload}")
            return
        
        logger.info(f"Creating order for reservation {reservation_id}")
        await create_order_from_event(  # Added await!
            db,
            user_id=user_id,
            reservation_id=reservation_id,
            showtime_id=showtime_id,
            seat_code=seat_code,
        )
        logger.info(f"✓ Order created successfully for reservation {reservation_id}")
    except Exception as e:
        logger.exception(f"Failed to create order from reservation: {e}")
    finally:
        db.close()


async def on_reservation_cancelled(payload: dict):
    logger.info(f"Order handler received reservation.cancelled: {payload}")
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
            await cancel_order_from_event(db, order_id=order.id)  # Added await!
    finally:
        db.close()


async def on_reservation_expired(payload: dict):
    logger.info(f"Order handler received reservation.expired: {payload}")
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
            await expire_order_from_event(db, order_id=order.id)  # Added await!
    finally:
        db.close()


async def on_pricing_snapshot_created(payload: dict):
    """Update order with pricing snapshot"""
    logger.info(f"💰 Order handler received pricing.snapshot_created: {payload}")
    
    order_id = payload.get("order_id")
    snapshot = payload.get("snapshot")
    
    if not order_id or not snapshot:
        logger.error(f"Missing order_id or snapshot in payload: {payload}")
        return
    
    db = SessionLocal()
    try:
        order = repo.get_order_by_id(db, order_id)
        if not order:
            logger.error(f"Order {order_id} not found")
            return
        
        # Update order with pricing info
        order.pricing_snapshot = snapshot
        order.final_amount = snapshot.get("final_price", 0)
        
        db.commit()
        db.refresh(order)
        
        logger.info(f"✓ Order {order_id} updated with final_amount: {order.final_amount}")
    except Exception as e:
        logger.exception(f"Failed to update order pricing: {e}")
        db.rollback()
    finally:
        db.close()


logger.info("Registering order event handlers...")
event_bus.subscribe("reservation.created", on_reservation_created)
event_bus.subscribe("reservation.cancelled", on_reservation_cancelled)
event_bus.subscribe("reservation.expired", on_reservation_expired)
event_bus.subscribe("pricing.snapshot_created", on_pricing_snapshot_created)
logger.info("✓ Order event handlers registered")