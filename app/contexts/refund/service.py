from sqlalchemy.orm import Session

from app.core.errors import ValidationError, NotFoundError, ConflictError
from app.shared.services.event_publisher import publish_event

from .models import Refund, RefundStatus
from app.contexts.payment.models import PaymentStatus
from .repository import RefundRepository
from app.contexts.payment.repository import PaymentRepository
from .events import (
    refund_issued_event,
    refund_failed_event
)

repo = RefundRepository()
payment_repo = PaymentRepository()


def issue_refund_from_event(
    db: Session,
    reservation_id: int,
    payment_attempt_id: int,
    reason: str
) -> Refund:
    
    payment_attempt = payment_repo.get_payment_attempt_by_id(db, payment_attempt_id)
    if not payment_attempt:
        raise NotFoundError("Payment attempt not found")
    

    if payment_attempt.status != PaymentStatus.SUCCEEDED:
        raise ConflictError("Payment attempt not successful")
    

    existing_refunds = repo.list_refunds_for_reservation(db, reservation_id)
    if existing_refunds:
        raise ConflictError("Refund already issued for this reservation")


    refund = Refund(
        reservation_id=reservation_id,
        payment_attempt_id=payment_attempt_id,
        reason=reason
    )
    
    refund.amount = payment_attempt.final_amount


    repo.create_refund(db, refund)
    

    event = refund_issued_event(
        refund_id=refund.id,
        reservation_id=reservation_id,
        payment_attempt_id=payment_attempt.id,
        amount=refund.amount
    )
    publish_event(event["type"], event["payload"])

    return refund
