# app/contexts/payment/router.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from ..auth.dependencies import get_current_user
from ..order.repository import OrderRepository
from .schemas import PaymentAttemptRead
from .service import PaymentService

router = APIRouter(
    prefix="/payments",
    tags=["payments"],
)

# Create service instance
payment_service = PaymentService()
order_repo = OrderRepository()


@router.post("/order/{order_id}/initiate", response_model=PaymentAttemptRead)
async def initiate_payment_route(
    order_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """Initiate a payment for an order"""
    # Get the order to fetch its final_amount
    order = order_repo.get_by_id(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Verify order belongs to current_user
    if order.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to pay for this order")
    
    # Use the order's final_amount
    return await payment_service.create_payment_attempt(
        db=db,
        order_id=order_id,
        final_amount=order.final_amount
    )


@router.post("/{payment_attempt_id}/confirm", response_model=PaymentAttemptRead)
async def confirm_payment_route(
    payment_attempt_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """Confirm/complete a payment (mock payment processor)"""
    # In production, this would verify with Stripe/PayPal/etc
    # For testing, we just mark it as succeeded
    
    provider_payment_id = f"mock_payment_{payment_attempt_id}"
    
    return await payment_service.mark_payment_succeeded(
        db=db,
        payment_attempt_id=payment_attempt_id,
        provider_payment_id=provider_payment_id
    )


@router.get("/order/{order_id}", response_model=list[PaymentAttemptRead])
def list_payment_attempts_for_order_route(
    order_id: int,
    db: Session = Depends(get_db),
):
    return payment_service.list_payment_attempts_for_order(
        db=db,
        order_id=order_id,
    )


@router.get("/{payment_attempt_id}", response_model=PaymentAttemptRead)
def get_payment_attempt_by_id_route(
    payment_attempt_id: int,
    db: Session = Depends(get_db),
):
    return payment_service.get_payment_attempt(
        db=db,
        payment_attempt_id=payment_attempt_id,
    )