# app/contexts/audit/handlers.py

from app.core.database import SessionLocal
from app.core.event_bus import event_bus

from .service import write_audit_log


async def on_reservation_created(payload: dict):
    db = SessionLocal()
    try:
        write_audit_log(
            db=db,
            actor_id=payload.get("user_id"),
            actor_type="user",
            action="reservation.created",
            target_type="reservation",
            target_id=payload["reservation_id"],
            payload=payload,
        )
    finally:
        db.close()


async def on_reservation_cancelled(payload: dict):
    db = SessionLocal()
    try:
        write_audit_log(
            db=db,
            actor_id=payload.get("user_id"),
            actor_type="user",
            action="reservation.cancelled",
            target_type="reservation",
            target_id=payload["reservation_id"],
            payload=payload,
        )
    finally:
        db.close()


async def on_payment_succeeded(payload: dict):
    db = SessionLocal()
    try:
        # Get user_id from payload (will be added in Fix 1)
        user_id = payload.get("user_id")
        
        write_audit_log(
            db=db,
            actor_id=user_id,  # Use the user_id from payment event
            actor_type="user",
            action="payment.succeeded",
            target_type="order",
            target_id=payload["order_id"],
            payload=payload,
        )
    finally:
        db.close()


async def on_payment_failed(payload: dict):
    db = SessionLocal()
    try:
        # Get user_id from payload (will be added in Fix 1)
        user_id = payload.get("user_id")
        
        write_audit_log(
            db=db,
            actor_id=user_id,  # Use the user_id from payment event
            actor_type="user",
            action="payment.failed",
            target_type="order",
            target_id=payload["order_id"],
            payload=payload,
        )
    finally:
        db.close()


async def on_refund_issued(payload: dict):
    db = SessionLocal()
    try:
        write_audit_log(
            db=db,
            actor_id=None,
            actor_type="system",
            action="refund.issued",
            target_type="refund",
            target_id=payload["refund_id"],
            payload=payload,
        )
    finally:
        db.close()



event_bus.subscribe("reservation.created", on_reservation_created)
event_bus.subscribe("reservation.cancelled", on_reservation_cancelled)
event_bus.subscribe("payment.succeeded", on_payment_succeeded)
event_bus.subscribe("payment.failed", on_payment_failed)
event_bus.subscribe("refund.issued", on_refund_issued)