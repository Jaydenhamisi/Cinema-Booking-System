# app/contexts/screen/events.py

"""
Domain events for the ScreenContext.

Event shape:
{
    "type": "<context.action>",
    "payload": {...}
}
"""


# ----- Screen Events -----


def screen_created_event(screen_id: int) -> dict:
    return {
        "type": "screen.created",
        "payload": {"screen_id": screen_id},
    }


def screen_updated_event(screen_id: int) -> dict:
    return {
        "type": "screen.updated",
        "payload": {"screen_id": screen_id},
    }


def screen_deleted_event(screen_id: int) -> dict:
    return {
        "type": "screen.deleted",
        "payload": {"screen_id": screen_id},
    }


# ----- Seat Layout Events -----


def layout_created_event(layout_id: int) -> dict:
    return {
        "type": "screen.layout_created",
        "payload": {"layout_id": layout_id},
    }


def layout_updated_event(layout_id: int) -> dict:
    return {
        "type": "screen.layout_updated",
        "payload": {"layout_id": layout_id},
    }


def layout_deleted_event(layout_id: int) -> dict:
    return {
        "type": "screen.layout_deleted",
        "payload": {"layout_id": layout_id},
    }
