# app/contexts/payment/events.py

"""
Domain events emitted by PaymentContext.
"""


def payment_attempt_pending_event(
    payment_attempt_id: int,
    order_id: int,
    amount_attempted: float,
    final_amount: float
) -> dict:
    return {
        "type": "payment.pending",
        "payload": {
            "payment_attempt_id": payment_attempt_id,
            "order_id": order_id,
            "amount_attempted": amount_attempted,
            "final_amount": final_amount,
        },
    }


def payment_attempt_succeeded_event(
    payment_attempt_id: int,
    order_id: int,
    final_amount: float
) -> dict:
    return {
        "type": "payment.succeeded",
        "payload": {
            "payment_attempt_id": payment_attempt_id,
            "order_id": order_id,
            "final_amount": final_amount,
        },
    }


def payment_attempt_failed_event(
    payment_attempt_id: int,
    order_id: int,
    failure_reason: str
) -> dict:
    return {
        "type": "payment.failed",
        "payload": {
            "payment_attempt_id": payment_attempt_id,
            "order_id": order_id,
            "failure_reason": failure_reason,
        },
    }