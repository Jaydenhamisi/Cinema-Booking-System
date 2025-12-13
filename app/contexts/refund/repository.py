from sqlalchemy.orm import Session
from sqlalchemy import select

from .models import Refund


class RefundRepository:

    def create_refund(
        self,
        db: Session,
        refund: Refund
    ):
        db.add(refund)
        db.commit()
        db.refresh(refund)
        return refund
    

    def get_refund_by_id(
        self,
        db: Session,
        refund_id: int 
    ):
        return db.get(Refund, refund_id)
    

    def list_refunds_for_reservation(
        self,
        db: Session,
        reservation_id: int
    ):
        stmt = select(Refund).where(Refund.reservation_id == reservation_id)
        return db.scalars(stmt).all()
    

    def save(
        self,
        db: Session,
        refund: Refund 
    ):
        db.add(refund)
        db.commit()
        db.refresh(refund)
        return refund