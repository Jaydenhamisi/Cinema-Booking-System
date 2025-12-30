from sqlalchemy.orm import Session
from sqlalchemy import select

from .models import RefundRequest


class RefundRepository:

    def create(self, db: Session, refund_request: RefundRequest):
        db.add(refund_request)
        db.commit()
        db.refresh(refund_request)
        return refund_request

    def get_by_id(self, db: Session, refund_request_id: int):
        return db.get(RefundRequest, refund_request_id)

    def list_by_payment_attempt_id(self, db: Session, payment_attempt_id: int):
        stmt = select(RefundRequest).where(RefundRequest.payment_attempt_id == payment_attempt_id)
        return db.scalars(stmt).all()

    def list_by_reservation_id(self, db: Session, reservation_id: int):
        stmt = select(RefundRequest).where(RefundRequest.reservation_id == reservation_id)
        return db.scalars(stmt).all()

    def save(self, db: Session, refund_request: RefundRequest):
        db.add(refund_request)
        db.commit()
        db.refresh(refund_request)
        return refund_request