# app/contexts/seat_availability/events.py

from datetime import datetime

"""
Domain events emitted by SeatAvailabilityContext.
"""

def seat_locked_event(showtime_id: int, seat_code: str, user_id: int, expires_at: datetime) -> dict:
    return {
        "type": "seat.locked",
        "payload": {
            "showtime_id": showtime_id,
            "seat_code": seat_code,
            "user_id": user_id,
            "expires_at": expires_at,
        },
    }


def seat_unlocked_event(showtime_id: int, seat_code: str) -> dict:
    return {
        "type": "seat.unlocked",
        "payload": {
            "showtime_id": showtime_id,
            "seat_code": seat_code,
        },
    }


def seat_expired_event(showtime_id: int, seat_code: str) -> dict:
    return {
        "type": "seat.expired",
        "payload": {
            "showtime_id": showtime_id,
            "seat_code": seat_code,
        },
    }


def seat_reserved_event(showtime_id: int, seat_code: str) -> dict:
    return {
        "type": "seat.reserved",
        "payload": {
            "showtime_id": showtime_id,
            "seat_code": seat_code,
        },
    }
