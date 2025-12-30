from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.contexts.auth.dependencies import get_current_admin
from app.contexts.user.service import UserProfileService
from app.contexts.user.schemas import UserProfileResponse, AdminUpdateUserType

from .service import (
    force_cancel_reservation,
    force_cancel_order,
    force_fail_payment,
    force_refund,
)

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
)


@router.post("/reservations/{reservation_id}/cancel")
def admin_force_cancel_reservation(
    reservation_id: int,
    current_admin=Depends(get_current_admin),
):
    force_cancel_reservation(reservation_id)
    return {"status": "ok"}


@router.post("/orders/{order_id}/cancel")
def admin_force_cancel_order(
    order_id: int,
    current_admin=Depends(get_current_admin),
):
    force_cancel_order(order_id)
    return {"status": "ok"}


@router.post("/payments/{payment_attempt_id}/fail")
async def admin_force_fail_payment(  # Make async
    payment_attempt_id: int,
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin),
):
    from app.contexts.payment.service import PaymentService
    service = PaymentService()
    return await service.mark_payment_failed(  # Await it
        db,
        payment_attempt_id=payment_attempt_id,
        failure_reason="Admin forced failure"
    )


@router.post("/refunds/force")
def admin_force_refund(
    reservation_id: int,
    payment_attempt_id: int,
    reason: str,
    current_admin=Depends(get_current_admin),
):
    force_refund(
        reservation_id=reservation_id,
        payment_attempt_id=payment_attempt_id,
        reason=reason,
    )
    return {"status": "ok"}


# ===== User Profile Admin Routes =====

@router.get("/users/{user_id}/profile", response_model=UserProfileResponse)
def get_user_profile(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin),
):
    """Admin views any user's profile"""
    service = UserProfileService()
    return service.get_profile(db, user_id)


@router.patch("/users/{user_id}/type", response_model=UserProfileResponse)
def update_user_type(
    user_id: int,
    payload: AdminUpdateUserType,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin),
):
    """Admin changes user's type (promote to admin / demote to user)"""
    service = UserProfileService()
    return service.admin_update_user_type(db, user_id, payload.user_type)


@router.delete("/users/{user_id}/profile", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_profile(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin),
):
    """Admin deletes user profile"""
    service = UserProfileService()
    service.delete_profile(db, user_id)
    # 204 No Content - successful deletion, no response body



@router.post("/showtimes/{showtime_id}/cancel")
async def admin_cancel_showtime(  # Make it async
    showtime_id: int,
    reason: str = None,
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin),
):
    from app.contexts.showtime.service import ShowtimeService
    service = ShowtimeService()
    return await service.cancel_showtime(  # Await it
        db, 
        showtime_id, 
        reason=reason,
        user_id=current_admin.id
    )

@router.post("/refunds/{refund_request_id}/approve")
async def admin_approve_refund(  # Make async
    refund_request_id: int,
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin),
):
    from app.contexts.refund.service import RefundService
    service = RefundService()
    return await service.approve_refund(  # Await it
        db,
        refund_request_id=refund_request_id,
        user_id=current_admin.id,  # Pass admin's user_id
    )


@router.post("/refunds/{refund_request_id}/reject")
async def admin_reject_refund(  # Make async
    refund_request_id: int,
    rejection_reason: str,
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin),
):
    from app.contexts.refund.service import RefundService
    service = RefundService()
    return await service.reject_refund(  # Await it
        db,
        refund_request_id=refund_request_id,
        rejection_reason=rejection_reason,
        user_id=current_admin.id,  # Pass admin's user_id
    )