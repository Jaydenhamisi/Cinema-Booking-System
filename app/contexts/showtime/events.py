# app/contexts/showtime/events.py

"""
Domain events emitted by ShowtimeContext.
"""

# -----------------------------
# BASIC EVENTS
# -----------------------------

def showtime_created_event(showtime_id: int, user_id: int = None) -> dict:
    return {
        "type": "showtime.created",
        "payload": {
            "showtime_id": showtime_id,
            "user_id": user_id,
        },
    }


def showtime_updated_event(showtime_id: int, user_id: int = None) -> dict:
    return {
        "type": "showtime.updated",
        "payload": {
            "showtime_id": showtime_id,
            "user_id": user_id,
        },
    }


def showtime_deleted_event(showtime_id: int, user_id: int = None) -> dict:
    return {
        "type": "showtime.deleted",
        "payload": {
            "showtime_id": showtime_id,
            "user_id": user_id,
        },
    }


# -----------------------------
# BUSINESS EVENTS
# -----------------------------

def showtime_cancelled_event(
    showtime_id: int, 
    reason: str = None, 
    user_id: int = None
) -> dict:
    return {
        "type": "showtime.cancelled",
        "payload": {
            "showtime_id": showtime_id,
            "reason": reason,
            "user_id": user_id,
        },
    }


def showtime_time_changed_event(
    showtime_id: int, 
    old_start, 
    new_start,
    user_id: int = None
) -> dict:
    return {
        "type": "showtime.time_changed",
        "payload": {
            "showtime_id": showtime_id,
            "old_start_time": old_start,
            "new_start_time": new_start,
            "user_id": user_id,
        },
    }