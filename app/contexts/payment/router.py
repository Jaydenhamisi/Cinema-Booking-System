from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from .schemas import PaymentAttemptRead
from .repository import PaymentRepository

repo = PaymentRepository()

router = APIRouter(
    prefix="/payments",
    tags=["payments"],
)


@router.get("/order/{order_id}", response_model=list[PaymentAttemptRead])
def list_payment_attempts_for_order_route(
    order_id: int,
    db: Session = Depends(get_db),
):
    return repo.list_payment_attempts_for_order(
        db=db,
        order_id=order_id,
    )


@router.get("/{payment_attempt_id}", response_model=PaymentAttemptRead)
def get_payment_attempt_by_id_route(
    payment_attempt_id: int,
    db: Session = Depends(get_db),
):
    return repo.get_payment_attempt_by_id(
        db=db,
        payment_attempt_id=payment_attempt_id,
    )