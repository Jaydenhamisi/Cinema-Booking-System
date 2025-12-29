# app/shared/services/event_publisher.py

import asyncio
import logging
from typing import Any, Dict

from app.core.event_bus import event_bus

logger = logging.getLogger(__name__)


def publish_event(event_type: str, payload: Dict[str, Any]) -> None:
    """
    Synchronous domain event publisher for use in sync code.
    """
    logger.info(f"📢 Publishing event: {event_type} with payload: {payload}")
    asyncio.run(event_bus.publish(event_type, payload))


async def publish_event_async(event_type: str, payload: Dict[str, Any]) -> None:
    """
    Async domain event publisher for use in async handlers.
    """
    logger.info(f"📢 Publishing event: {event_type} with payload: {payload}")
    await event_bus.publish(event_type, payload)