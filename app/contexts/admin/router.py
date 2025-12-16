from fastapi import APIRouter, Depends

from app.contexts.auth.dependencies import get_current_admin

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
def admin_force_fail_payment(
    payment_attempt_id: int,
    current_admin=Depends(get_current_admin),
):
    force_fail_payment(payment_attempt_id)
    return {"status": "ok"}


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
