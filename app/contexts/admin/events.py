"""
Admin command events.

These events represent admin intent.
They do NOT represent outcomes.
"""


def admin_force_cancel_reservation_event(reservation_id: int) -> dict:
    return {
        "type": "admin.force_cancel_reservation",
        "payload": {
            "reservation_id": reservation_id,
        },
    }


def admin_force_cancel_order_event(order_id: int) -> dict:
    return {
        "type": "admin.force_cancel_order",
        "payload": {
            "order_id": order_id,
        },
    }


def admin_force_fail_payment_event(payment_attempt_id: int) -> dict:
    return {
        "type": "admin.force_fail_payment",
        "payload": {
            "payment_attempt_id": payment_attempt_id,
        },
    }


def admin_force_refund_event(
    reservation_id: int,
    payment_attempt_id: int,
    reason: str,
) -> dict:
    return {
        "type": "admin.force_refund",
        "payload": {
            "reservation_id": reservation_id,
            "payment_attempt_id": payment_attempt_id,
            "reason": reason,
        },
    }
