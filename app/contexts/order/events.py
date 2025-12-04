# app/contexts/order/events.py

"""
Domain events emitted by OrderContext.
"""


def order_created_event(
    order_id: int,
    reservation_id: int,
    user_id: int,
    showtime_id: int,
    seat_code: str,
) -> dict:
    return {
        "type": "order.created",
        "payload": {
            "order_id": order_id,
            "reservation_id": reservation_id,
            "user_id": user_id,
            "showtime_id": showtime_id,
            "seat_code": seat_code,
        },
    }


def order_completed_event(order_id: int) -> dict:
    return {
        "type": "order.completed",
        "payload": {
            "order_id": order_id,
        },
    }


def order_cancelled_event(order_id: int) -> dict:
    return {
        "type": "order.cancelled",
        "payload": {
            "order_id": order_id,
        },
    }


def order_expired_event(order_id: int) -> dict:
    return {
        "type": "order.expired",
        "payload": {
            "order_id": order_id,
        },
    }
