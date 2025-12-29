from sqlalchemy.orm import Session

from app.core.errors import ValidationError, NotFoundError, ConflictError
from app.shared.services.event_publisher import publish_event

from .models import PaymentAttempt, PaymentStatus
from .repository import PaymentRepository
from .events import (
    payment_attempt_pending_event,
    payment_attempt_succeeded_event,
    payment_attempt_failed_event
)

repo = PaymentRepository()



def create_payment_attempt(
    db: Session,
    order_id: int,
    final_amount: float 
) -> PaymentAttempt:
    
    payment_attempt = PaymentAttempt(
        order_id=order_id,
        status=PaymentStatus.PENDING,
        amount_attempted=final_amount,
        final_amount=final_amount
    )

    payment_attempt = repo.create_payment_attempt(db, payment_attempt)

    # Get user_id from the order
    order = payment_attempt.order  # Assuming relationship exists
    
    event = payment_attempt_pending_event(
        payment_attempt_id=payment_attempt.id,
        order_id=order_id,
        amount_attempted=final_amount,
        final_amount=final_amount,
        user_id=order.user_id  # ADD THIS
    )
    publish_event(event["type"], event["payload"])

    return payment_attempt



def mark_payment_succeeded(
    db: Session,
    payment_attempt_id: int,
    provider_payment_id: str 
):
    payment_attempt = repo.get_payment_attempt_by_id(db, payment_attempt_id)
    if not payment_attempt:
        raise NotFoundError("Payment attempt not found")
    
    if payment_attempt.status == PaymentStatus.SUCCEEDED:
        raise ConflictError("Payment attempt already succeeded")
    
    if payment_attempt.status == PaymentStatus.FAILED:
        raise ConflictError("Payment attempt has failed")
    
    if payment_attempt.status != PaymentStatus.PENDING:
        raise ConflictError("Payment attempt not pending")

    order = payment_attempt.order
    
    if payment_attempt.final_amount != order.final_amount:
        raise ValidationError("Final amount not equal to order amount")
    
    payment_attempt.status = PaymentStatus.SUCCEEDED

    payment_attempt.provider_payment_id = provider_payment_id

    repo.save(db, payment_attempt)

    event = payment_attempt_succeeded_event(
        payment_attempt_id=payment_attempt_id,
        order_id=order.id,
        final_amount=payment_attempt.final_amount,
        user_id=order.user_id  # ADD THIS
    )
    publish_event(event["type"], event["payload"])

    return payment_attempt



def mark_payment_failed(
    db: Session,
    payment_attempt_id: int,
    failure_reason: str
):
    payment_attempt = repo.get_payment_attempt_by_id(db, payment_attempt_id)
    if not payment_attempt:
        raise NotFoundError("Payment attempt not found")
    
    if payment_attempt.status == PaymentStatus.SUCCEEDED:
        raise ConflictError("Payment attempt already succeeded")
    
    if payment_attempt.status == PaymentStatus.FAILED:
        raise ConflictError("Payment attempt already Failed")
    
    if payment_attempt.status != PaymentStatus.PENDING:
        raise ConflictError("Payment attempt not pending")
    
    payment_attempt.status = PaymentStatus.FAILED

    payment_attempt.failure_reason = failure_reason

    repo.save(db, payment_attempt)

    # Get order for user_id
    order = payment_attempt.order  # ADD THIS

    event = payment_attempt_failed_event(
        payment_attempt_id=payment_attempt_id,
        failure_reason=payment_attempt.failure_reason,
        order_id=payment_attempt.order_id,
        user_id=order.user_id  # ADD THIS
    )
    publish_event(event["type"], event["payload"])

    return payment_attempt