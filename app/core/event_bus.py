# app/core/event_bus.py
import asyncio
import logging
from collections import defaultdict
from typing import Any, Awaitable, Callable, Dict, List

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

    async def publish(self, event_type: str, payload: Dict[str, Any]) -> None:
        handlers = self.subscribers.get(event_type, [])

        for handler in handlers:
            asyncio.create_task(self._safe_invoke(handler, event_type, payload))

    async def _safe_invoke(self, handler: EventHandler, event_type: str, payload: Dict[str, Any]) -> None:
        try:
            await handler(payload)
        except Exception as e:
            logger.exception(f"Event handler failed: {event_type} -> {handler.__name__}")


event_bus = EventBus()
