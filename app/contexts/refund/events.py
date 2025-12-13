"""
Domain events emitted by RefundContext
"""


def refund_issued_event(
    refund_id: int,
    reservation_id: int,
    payment_attempt_id: int,
    amount: float
) -> dict:
    return {
        "type": "refund.issued",
        "payload": {
            "refund_id": refund_id,
            "reservation_id": reservation_id,
            "payment_attempt_id": payment_attempt_id,
            "amount": amount,
        },
    }


def refund_failed_event(
    refund_id: int,
    reservation_id: int,
    payment_attempt_id: int,
    failure_reason: str
) -> dict:
    return {
        "type": "refund.failed",
        "payload": {
            "refund_id": refund_id,
            "reservation_id": reservation_id,
            "payment_attempt_id": payment_attempt_id,
            "failure_reason": failure_reason,
        },
    }