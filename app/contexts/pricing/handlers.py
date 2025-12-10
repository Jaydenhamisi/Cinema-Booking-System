# app/contexts/pricing/handlers.py

from app.core.database import SessionLocal
from app.core.event_bus import event_bus

from .service import create_snapshot_from_event


async def on_order_created(payload: dict):
    """
    Triggered when OrderContext emits 'order.created'.
    PricingContext should compute pricing snapshot.
    """
    order_id = payload.get("order_id")

    if not order_id:
        return  # malformed event

    db = SessionLocal()
    try:
        create_snapshot_from_event(
            db=db,
            order_id=order_id,
        )
    finally:
        db.close()


# register with event bus
event_bus.subscribe("order.created", on_order_created)
