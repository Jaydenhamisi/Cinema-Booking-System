# app/contexts/reservation/events.py

"""
Domain events emitted by ReservationContext.
"""


def reservation_created_event(
    reservation_id: int,
    user_id: int,
    showtime_id: int,
    seat_code: str,
) -> dict:
    return {
        "type": "reservation.created",
        "payload": {
            "reservation_id": reservation_id,
            "user_id": user_id,
            "showtime_id": showtime_id,
            "seat_code": seat_code,
        },
    }


def reservation_cancelled_event(reservation_id: int) -> dict:
    return {
        "type": "reservation.cancelled",
        "payload": {
            "reservation_id": reservation_id,
        },
    }


def reservation_expired_event(reservation_id: int) -> dict:
    return {
        "type": "reservation.expired",
        "payload": {
            "reservation_id": reservation_id,
        },
    }
