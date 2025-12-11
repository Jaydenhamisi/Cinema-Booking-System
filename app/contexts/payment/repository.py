# app/contexts/payment/repository.py

from sqlalchemy.orm import Session
from sqlalchemy import select

from .models import PaymentAttempt

class PaymentRepository:

    def create_payment_attempt(
        self, 
        db: Session, 
        payment_attempt: PaymentAttempt
    ):
        db.add(payment_attempt)
        db.commit()
        db.refresh(payment_attempt)
        return payment_attempt
    

    def get_payment_attempt_by_id(
        self,
        db: Session,
        payment_attempt_id: int 
    ):
        return db.get(PaymentAttempt, payment_attempt_id)
    

    def list_payment_attempts_for_order(self, db: Session, order_id: int):
        stmt = select(PaymentAttempt).where(PaymentAttempt.order_id == order_id)
        return db.scalars(stmt).all()
    

    def save(self, db: Session, payment_attempt: PaymentAttempt):
        db.add(payment_attempt)
        db.commit()
        db.refresh(payment_attempt)
        return payment_attempt

    
