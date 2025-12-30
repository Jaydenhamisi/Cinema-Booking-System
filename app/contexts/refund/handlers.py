# app/contexts/refund/handlers.py
import logging
from typing import Dict, Any

from app.core.database import SessionLocal
from app.core.event_bus import event_bus

from .service import RefundService

logger = logging.getLogger(__name__)

# Create service instance
refund_service = RefundService()


async def on_refund_approved(payload: Dict[str, Any]) -> None:
    """
    When a refund is approved, mark it as completed (mock refund processing).
    In production, this would integrate with payment processor.
    """
    refund_request_id = payload.get("refund_request_id")
    user_id = payload.get("user_id")

    if not refund_request_id:
        logger.warning("⚠️ Received refund.request_approved without refund_request_id")
        return

    logger.info(f"💳 Processing approved refund {refund_request_id}")

    db = SessionLocal()
    try:
        # Mock provider refund ID
        provider_refund_id = f"mock_refund_{refund_request_id}"
        
        await refund_service.complete_refund(
            db=db,
            refund_request_id=refund_request_id,
            provider_refund_id=provider_refund_id,
            user_id=user_id,
        )
        logger.info(f"✓ Refund {refund_request_id} completed with provider ID: {provider_refund_id}")
    except Exception as e:
        logger.error(f"❌ Failed to complete refund {refund_request_id}: {e}")
        raise
    finally:
        db.close()


# Register with event bus
event_bus.subscribe("refund.request_approved", on_refund_approved)