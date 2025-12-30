# app/contexts/refund/router.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.contexts.auth.dependencies import get_current_user
from app.contexts.reservation.repository import ReservationRepository
from app.contexts.payment.repository import PaymentRepository

from .service import RefundService
from .schemas import RefundRead  

router = APIRouter(
    prefix="/refunds",
    tags=["refunds"],
)

# Create service instance
refund_service = RefundService()
reservation_repo = ReservationRepository()
payment_repo = PaymentRepository()


@router.post("/", response_model=RefundRead)
async def create_refund_request(
    reservation_id: int,
    payment_attempt_id: int,
    amount: float,
    reason: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """Create a refund request for a cancelled reservation."""
    # Verify reservation exists and belongs to user
    reservation = reservation_repo.get_by_id(db, reservation_id)
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")
    
    if reservation.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to request refund for this reservation")
    
    # Verify payment exists
    payment = payment_repo.get_payment_attempt_by_id(db, payment_attempt_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    return await refund_service.create_refund_request(
        db=db,
        payment_attempt_id=payment_attempt_id,
        reservation_id=reservation_id,
        amount=amount,
        reason=reason,
        user_id=current_user.id,
    )


@router.get("/payment/{payment_attempt_id}", response_model=list[RefundRead])
def list_refunds_for_payment(
    payment_attempt_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """List refunds for a payment."""
    return refund_service.list_refunds_for_payment(db, payment_attempt_id)


@router.get("/reservation/{reservation_id}", response_model=list[RefundRead])
def list_refunds_for_reservation(
    reservation_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """List refunds for a reservation."""
    return refund_service.list_refunds_for_reservation(db, reservation_id)


@router.get("/{refund_request_id}", response_model=RefundRead)
def get_refund_request(
    refund_request_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """Get a refund request by ID."""
    return refund_service.get_refund_request(db, refund_request_id)