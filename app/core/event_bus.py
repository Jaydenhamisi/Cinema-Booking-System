# app/core/event_bus.py

import asyncio
import logging
from collections import defaultdict
from typing import Callable, Dict, Any, List, Awaitable

logger = logging.getLogger(__name__)

EventHandler = Callable[[Dict[str, Any]], Awaitable[None]]


class EventBus:
    """
    Lightweight asynchronous in-memory event bus for domain events.
    """

    def __init__(self) -> None:
        self.subscribers: Dict[str, List[EventHandler]] = defaultdict(list)

    def subscribe(self, event_type: str, handler: EventHandler) -> None:
        self.subscribers[event_type].append(handler)
        logger.info(f"✓ Subscribed handler {handler.__name__} to event {event_type}")

    async def publish(self, event_type: str, payload: Dict[str, Any]) -> None:
        handlers = self.subscribers.get(event_type, [])
        
        logger.info(f"📨 Event bus publishing {event_type} to {len(handlers)} handlers")
        
        if not handlers:
            logger.warning(f"⚠️  No handlers registered for event: {event_type}")
            return

        # Wait for all handlers to complete (changed from create_task)
        for handler in handlers:
            logger.debug(f"Invoking handler: {handler.__name__} for {event_type}")
            await self._safe_invoke(handler, event_type, payload)

    async def _safe_invoke(self, handler: EventHandler, event_type: str, payload: Dict[str, Any]) -> None:
        try:
            logger.debug(f"Executing handler {handler.__name__}")
            await handler(payload)
            logger.info(f"✓ Handler {handler.__name__} completed successfully")
        except Exception as e:
            logger.exception(f"❌ Event handler failed: {event_type} -> {handler.__name__}: {e}")


event_bus = EventBus()