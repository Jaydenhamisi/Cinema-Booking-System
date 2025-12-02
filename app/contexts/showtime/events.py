# app/contexts/showtime/events.py

"""
Domain events emitted by ShowtimeContext.
"""

# -----------------------------
# BASIC EVENTS
# -----------------------------
def showtime_created_event(showtime_id: int) -> dict:
    return {
        "type": "showtime.created",
        "payload": {"showtime_id": showtime_id},
    }


def showtime_updated_event(showtime_id: int) -> dict:
    return {
        "type": "showtime.updated",
        "payload": {"showtime_id": showtime_id},
    }


def showtime_deleted_event(showtime_id: int) -> dict:
    return {
        "type": "showtime.deleted",
        "payload": {"showtime_id": showtime_id},
    }


# -----------------------------
# FUTURE EVENTS
# -----------------------------
def showtime_cancelled_event(showtime_id: int, reason: str | None = None) -> dict:
    return {
        "type": "showtime.cancelled",
        "payload": {
            "showtime_id": showtime_id,
            "reason": reason,
        },
    }


def showtime_time_changed_event(showtime_id: int, old_start, new_start) -> dict:
    return {
        "type": "showtime.time_changed",
        "payload": {
            "showtime_id": showtime_id,
            "old_start_time": old_start,
            "new_start_time": new_start,
        },
    }
