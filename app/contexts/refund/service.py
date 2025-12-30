# app/contexts/refund/service.py
from sqlalchemy.orm import Session

from app.core.errors import NotFoundError, ConflictError
from app.shared.services.event_publisher import publish_event_async

from .models import RefundRequest, RefundStatus
from .repository import RefundRepository
from .events import (
    refund_request_created_event,
    refund_request_approved_event,
    refund_request_rejected_event,
    refund_request_completed_event,
)


class RefundService:
    """Service for Refund business logic."""
    
    def __init__(self):
        self.repo = RefundRepository()

    async def create_refund_request(
        self,
        db: Session,
        payment_attempt_id: int,
        reservation_id: int,
        amount: float,
        reason: str,
        user_id: int,
    ) -> RefundRequest:
        """Create a new refund request."""
        refund_request = RefundRequest(
            payment_attempt_id=payment_attempt_id,
            reservation_id=reservation_id,
            amount=amount,
            reason=reason,
            status=RefundStatus.PENDING,
        )

        refund_request = self.repo.create(db, refund_request)

        event = refund_request_created_event(
            refund_request_id=refund_request.id,
            payment_attempt_id=payment_attempt_id,
            reservation_id=reservation_id,
            amount=amount,
            reason=reason,
            user_id=user_id,
        )
        await publish_event_async(event["type"], event["payload"])

        return refund_request

    async def approve_refund(
        self,
        db: Session,
        refund_request_id: int,
        user_id: int = None,
    ) -> RefundRequest:
        """Approve a refund request."""
        refund_request = self.repo.get_by_id(db, refund_request_id)
        if not refund_request:
            raise NotFoundError("Refund request not found")

        if refund_request.status != RefundStatus.PENDING:
            raise ConflictError(f"Refund request is not pending (current: {refund_request.status})")

        refund_request.status = RefundStatus.APPROVED
        refund_request = self.repo.save(db, refund_request)

        event = refund_request_approved_event(
            refund_request_id=refund_request.id,
            user_id=user_id,
        )
        await publish_event_async(event["type"], event["payload"])

        return refund_request

    async def reject_refund(
        self,
        db: Session,
        refund_request_id: int,
        rejection_reason: str,
        user_id: int = None,
    ) -> RefundRequest:
        """Reject a refund request."""
        refund_request = self.repo.get_by_id(db, refund_request_id)
        if not refund_request:
            raise NotFoundError("Refund request not found")

        if refund_request.status != RefundStatus.PENDING:
            raise ConflictError(f"Refund request is not pending (current: {refund_request.status})")

        refund_request.status = RefundStatus.REJECTED
        refund_request.rejection_reason = rejection_reason
        refund_request = self.repo.save(db, refund_request)

        event = refund_request_rejected_event(
            refund_request_id=refund_request.id,
            rejection_reason=rejection_reason,
            user_id=user_id,
        )
        await publish_event_async(event["type"], event["payload"])

        return refund_request

    async def complete_refund(
        self,
        db: Session,
        refund_request_id: int,
        provider_refund_id: str,
        user_id: int = None,
    ) -> RefundRequest:
        """Complete a refund (mark as processed)."""
        refund_request = self.repo.get_by_id(db, refund_request_id)
        if not refund_request:
            raise NotFoundError("Refund request not found")

        if refund_request.status != RefundStatus.APPROVED:
            raise ConflictError(f"Refund request is not approved (current: {refund_request.status})")

        refund_request.status = RefundStatus.COMPLETED
        refund_request.provider_refund_id = provider_refund_id
        refund_request = self.repo.save(db, refund_request)

        event = refund_request_completed_event(
            refund_request_id=refund_request.id,
            provider_refund_id=provider_refund_id,
            user_id=user_id,
        )
        await publish_event_async(event["type"], event["payload"])

        return refund_request
    
    # ===== READ OPERATIONS (sync) =====
    
    def get_refund_request(self, db: Session, refund_request_id: int):
        """Get refund request by ID."""
        refund_request = self.repo.get_by_id(db, refund_request_id)
        if not refund_request:
            raise NotFoundError("Refund request not found")
        return refund_request
    
    def list_refunds_for_payment(self, db: Session, payment_attempt_id: int):
        """List refunds for a payment."""
        return self.repo.list_by_payment_attempt_id(db, payment_attempt_id)
    
    def list_refunds_for_reservation(self, db: Session, reservation_id: int):
        """List refunds for a reservation."""
        return self.repo.list_by_reservation_id(db, reservation_id)