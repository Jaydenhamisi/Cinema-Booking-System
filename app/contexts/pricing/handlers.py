# app/contexts/pricing/handlers.py
import logging
from typing import Dict, Any

from app.core.database import SessionLocal
from app.core.event_bus import event_bus

from .service import PricingService

logger = logging.getLogger(__name__)

# Create service instance
pricing_service = PricingService()


async def on_order_created(payload: Dict[str, Any]) -> None:
    """
    Triggered when OrderContext emits 'order.created'.
    PricingContext computes pricing snapshot.
    """
    order_id = payload.get("order_id")

    if not order_id:
        logger.warning("⚠️ Received order.created event without order_id")
        return

    logger.info(f"💰 Pricing handler received order.created for order {order_id}")

    db = SessionLocal()
    try:
        result = await pricing_service.create_snapshot_from_event(
            db=db,
            order_id=order_id,
        )
        logger.info(f"✓ Pricing snapshot created for order {order_id}: final_price={result.final_price}")
    except Exception as e:
        logger.error(f"❌ Failed to create pricing snapshot for order {order_id}: {e}")
        raise
    finally:
        db.close()


# Register with event bus
event_bus.subscribe("order.created", on_order_created)