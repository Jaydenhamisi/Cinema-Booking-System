# app/contexts/payment/handlers.py

from app.core.database import SessionLocal
from app.core.event_bus import event_bus

from app.contexts.order.service import complete_order_from_event

async def on_payment_succeeded(payload: dict):
    order_id = payload.get("order_id")

    if not order_id:
        return
    
    db = SessionLocal()
    try:
        complete_order_from_event(db, order_id)
    finally:
        db.close()

event_bus.subscribe("payment.succeeded", on_payment_succeeded)


async def on_payment_failed(payload: dict):
    order_id = payload.get("order_id")

    if not order_id:
        return
    
event_bus.subscribe("payment.failed", on_payment_failed)
