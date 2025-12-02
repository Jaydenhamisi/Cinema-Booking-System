# app/contexts/screen/handlers.py

"""
ScreenContext subscribes to no inbound domain events in the current DDD plan.

It only emits:
- screen.created
- screen.updated
- screen.deleted
- screen.layout_created
- screen.layout_updated
- screen.layout_deleted
"""


def register_handlers() -> None:
    """
    Kept for consistency with other contexts.
    No subscriptions to register yet.
    """
    return None
