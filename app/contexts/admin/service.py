from app.shared.services.event_publisher import publish_event

from .events import (
    admin_force_cancel_reservation_event,
    admin_force_cancel_order_event,
    admin_force_fail_payment_event,
    admin_force_refund_event,
)


def force_cancel_reservation(reservation_id: int) -> None:
    event = admin_force_cancel_reservation_event(reservation_id)
    publish_event(event["type"], event["payload"])


def force_cancel_order(order_id: int) -> None:
    event = admin_force_cancel_order_event(order_id)
    publish_event(event["type"], event["payload"])


def force_fail_payment(payment_attempt_id: int) -> None:
    event = admin_force_fail_payment_event(payment_attempt_id)
    publish_event(event["type"], event["payload"])


def force_refund(
    reservation_id: int,
    payment_attempt_id: int,
    reason: str,
) -> None:
    event = admin_force_refund_event(
        reservation_id=reservation_id,
        payment_attempt_id=payment_attempt_id,
        reason=reason,
    )
    publish_event(event["type"], event["payload"])
