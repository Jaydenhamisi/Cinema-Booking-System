from app.core.event_bus import event_bus

from .service import (
    send_booking_confirmation,
    send_payment_failure,
    send_refund_issued,
)


async def on_payment_succeeded(payload: dict):
    send_booking_confirmation(payload)


async def on_payment_failed(payload: dict):
    send_payment_failure(payload)


async def on_refund_issued(payload: dict):
    send_refund_issued(payload)


event_bus.subscribe("payment.succeeded", on_payment_succeeded)
event_bus.subscribe("payment.failed", on_payment_failed)
event_bus.subscribe("refund.issued", on_refund_issued)
