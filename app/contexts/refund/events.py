# app/contexts/refund/events.py

"""
Domain events emitted by RefundContext.
"""


def refund_request_created_event(
    refund_request_id: int,
    payment_attempt_id: int,
    reservation_id: int,
    amount: float,
    reason: str,
    user_id: int,
) -> dict:
    return {
        "type": "refund.request_created",
        "payload": {
            "refund_request_id": refund_request_id,
            "payment_attempt_id": payment_attempt_id,
            "reservation_id": reservation_id,
            "amount": amount,
            "reason": reason,
            "user_id": user_id,
        },
    }


def refund_request_approved_event(refund_request_id: int, user_id: int = None) -> dict:
    return {
        "type": "refund.request_approved",
        "payload": {
            "refund_request_id": refund_request_id,
            "user_id": user_id,
        },
    }


def refund_request_rejected_event(
    refund_request_id: int,
    rejection_reason: str,
    user_id: int = None,
) -> dict:
    return {
        "type": "refund.request_rejected",
        "payload": {
            "refund_request_id": refund_request_id,
            "rejection_reason": rejection_reason,
            "user_id": user_id,
        },
    }


def refund_request_completed_event(
    refund_request_id: int,
    provider_refund_id: str,
    user_id: int = None,
) -> dict:
    return {
        "type": "refund.request_completed",
        "payload": {
            "refund_request_id": refund_request_id,
            "provider_refund_id": provider_refund_id,
            "user_id": user_id,
        },
    }