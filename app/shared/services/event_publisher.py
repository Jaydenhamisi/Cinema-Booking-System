# app/shared/services/event_publisher.py

import asyncio
from typing import Any, Dict

from app.core.event_bus import event_bus


def publish_event(event_type: str, payload: Dict[str, Any]) -> None:
    """
    Fire-and-forget domain event publisher that works from both
    async and sync contexts.

    - If a running event loop exists: schedule event_bus.publish as a task.
    - If not: run it in a fresh event loop (blocking in that thread).
    """
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        # No running loop in this thread (e.g. FastAPI sync endpoint threadpool)
        asyncio.run(event_bus.publish(event_type, payload))
    else:
        loop.create_task(event_bus.publish(event_type, payload))
