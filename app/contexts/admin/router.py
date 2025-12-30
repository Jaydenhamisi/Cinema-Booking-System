from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.contexts.auth.dependencies import get_current_admin

# Schemas
from app.contexts.user.schemas import UserProfileResponse, AdminUpdateUserType
from app.contexts.movie.schemas import MovieCreate, MovieUpdate, MovieRead
from app.contexts.screen.schemas import (
    ScreenCreate, ScreenUpdate, ScreenRead,
    SeatLayoutCreate, SeatLayoutUpdate, SeatLayoutRead
)
from app.contexts.showtime.schemas import ShowtimeCreate, ShowtimeUpdate, ShowtimeRead

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
)


# ============================================================
# MOVIE ADMIN ROUTES
# ============================================================

@router.post("/movies", response_model=MovieRead)
async def admin_create_movie(
    payload: MovieCreate,
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin),
):
    """Admin creates a movie"""
    from app.contexts.movie.service import MovieService
    service = MovieService()
    
    return await service.create_movie(
        db=db,
        data=payload,
        user_id=current_admin.id,
    )


@router.put("/movies/{movie_id}", response_model=MovieRead)
async def admin_update_movie(
    movie_id: int,
    payload: MovieUpdate,
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin),
):
    """Admin updates a movie"""
    from app.contexts.movie.service import MovieService
    service = MovieService()
    
    return await service.update_movie(
        db=db,
        movie_id=movie_id,
        data=payload,
        user_id=current_admin.id,
    )


@router.delete("/movies/{movie_id}", status_code=status.HTTP_204_NO_CONTENT)
async def admin_delete_movie(
    movie_id: int,
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin),
):
    """Admin deletes a movie"""
    from app.contexts.movie.service import MovieService
    service = MovieService()
    
    await service.delete_movie(
        db=db,
        movie_id=movie_id,
        user_id=current_admin.id,
    )


@router.patch("/movies/{movie_id}/deactivate", response_model=MovieRead)
async def admin_deactivate_movie(
    movie_id: int,
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin),
):
    """Admin deactivates a movie"""
    from app.contexts.movie.service import MovieService
    service = MovieService()
    
    return await service.deactivate_movie(
        db=db,
        movie_id=movie_id,
        user_id=current_admin.id,
    )


# ============================================================
# SCREEN & LAYOUT ADMIN ROUTES
# ============================================================

@router.post("/screens", response_model=ScreenRead)
async def admin_create_screen(
    payload: ScreenCreate,
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin),
):
    """Admin creates a screen"""
    from app.contexts.screen.service import ScreenService
    service = ScreenService()
    
    return await service.create_screen(
        db=db,
        data=payload,
        user_id=current_admin.id,
    )


@router.put("/screens/{screen_id}", response_model=ScreenRead)
async def admin_update_screen(
    screen_id: int,
    payload: ScreenUpdate,
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin),
):
    """Admin updates a screen"""
    from app.contexts.screen.service import ScreenService
    service = ScreenService()
    
    return await service.update_screen(
        db=db,
        screen_id=screen_id,
        data=payload,
        user_id=current_admin.id,
    )


@router.delete("/screens/{screen_id}", status_code=status.HTTP_204_NO_CONTENT)
async def admin_delete_screen(
    screen_id: int,
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin),
):
    """Admin deletes a screen"""
    from app.contexts.screen.service import ScreenService
    service = ScreenService()
    
    await service.delete_screen(
        db=db,
        screen_id=screen_id,
        user_id=current_admin.id,
    )


@router.post("/layouts", response_model=SeatLayoutRead)
async def admin_create_layout(
    payload: SeatLayoutCreate,
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin),
):
    """Admin creates a seat layout"""
    from app.contexts.screen.service import ScreenService
    service = ScreenService()
    
    return await service.create_layout(
        db=db,
        data=payload,
        user_id=current_admin.id,
    )


@router.put("/layouts/{layout_id}", response_model=SeatLayoutRead)
async def admin_update_layout(
    layout_id: int,
    payload: SeatLayoutUpdate,
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin),
):
    """Admin updates a seat layout"""
    from app.contexts.screen.service import ScreenService
    service = ScreenService()
    
    return await service.update_layout(
        db=db,
        layout_id=layout_id,
        data=payload,
        user_id=current_admin.id,
    )


@router.delete("/layouts/{layout_id}", status_code=status.HTTP_204_NO_CONTENT)
async def admin_delete_layout(
    layout_id: int,
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin),
):
    """Admin deletes a seat layout"""
    from app.contexts.screen.service import ScreenService
    service = ScreenService()
    
    await service.delete_layout(
        db=db,
        layout_id=layout_id,
        user_id=current_admin.id,
    )


# ============================================================
# SHOWTIME ADMIN ROUTES
# ============================================================

@router.post("/showtimes", response_model=ShowtimeRead)
async def admin_create_showtime(
    payload: ShowtimeCreate,
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin),
):
    """Admin creates a showtime"""
    from app.contexts.showtime.service import ShowtimeService
    service = ShowtimeService()
    
    return await service.create_showtime(
        db=db,
        data=payload,
        user_id=current_admin.id,
    )


@router.put("/showtimes/{showtime_id}", response_model=ShowtimeRead)
async def admin_update_showtime(
    showtime_id: int,
    payload: ShowtimeUpdate,
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin),
):
    """Admin updates a showtime"""
    from app.contexts.showtime.service import ShowtimeService
    service = ShowtimeService()
    
    return await service.update_showtime(
        db=db,
        showtime_id=showtime_id,
        data=payload,
        user_id=current_admin.id,
    )


@router.delete("/showtimes/{showtime_id}", status_code=status.HTTP_204_NO_CONTENT)
async def admin_delete_showtime(
    showtime_id: int,
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin),
):
    """Admin deletes a showtime"""
    from app.contexts.showtime.service import ShowtimeService
    service = ShowtimeService()
    
    await service.delete_showtime(
        db=db,
        showtime_id=showtime_id,
        user_id=current_admin.id,
    )


@router.post("/showtimes/{showtime_id}/cancel")
async def admin_cancel_showtime(
    showtime_id: int,
    reason: str = None,
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin),
):
    """Admin cancels a showtime"""
    from app.contexts.showtime.service import ShowtimeService
    service = ShowtimeService()
    
    return await service.cancel_showtime(
        db=db,
        showtime_id=showtime_id,
        reason=reason,
        user_id=current_admin.id,
    )


@router.post("/showtimes/bulk-cancel")
async def admin_bulk_cancel_showtimes(
    screen_id: Optional[int] = Query(None),
    movie_id: Optional[int] = Query(None),
    reason: str = Query(...),
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin),
):
    """
    Admin bulk cancels showtimes for a screen or movie.
    Must provide either screen_id OR movie_id.
    """
    from app.contexts.showtime.service import ShowtimeService
    from app.core.errors import ValidationError
    
    if not screen_id and not movie_id:
        raise ValidationError("Must provide either screen_id or movie_id")
    
    if screen_id and movie_id:
        raise ValidationError("Provide only screen_id OR movie_id, not both")
    
    service = ShowtimeService()
    
    # Get showtimes to cancel
    if screen_id:
        showtimes = service.list_showtimes_for_screen(db, screen_id)
    else:
        showtimes = service.list_showtimes_for_movie(db, movie_id)
    
    # Cancel all active showtimes
    cancelled_count = 0
    for showtime in showtimes:
        if showtime.is_active:
            await service.cancel_showtime(
                db=db,
                showtime_id=showtime.id,
                reason=reason,
                user_id=current_admin.id,
            )
            cancelled_count += 1
    
    return {
        "cancelled_count": cancelled_count,
        "reason": reason,
        "screen_id": screen_id,
        "movie_id": movie_id,
    }


# ============================================================
# RESERVATION ADMIN ROUTES
# ============================================================

@router.post("/reservations/{reservation_id}/cancel")
async def admin_force_cancel_reservation(
    reservation_id: int,
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin),
):
    """Admin force cancels a reservation"""
    from app.contexts.reservation.service import ReservationService
    service = ReservationService()
    
    return await service.cancel_reservation(
        db=db,
        reservation_id=reservation_id,
        user_id=current_admin.id,
        allow_admin_override=True,
    )


# ============================================================
# ORDER ADMIN ROUTES
# ============================================================

@router.post("/orders/{order_id}/cancel")
async def admin_force_cancel_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin),
):
    """Admin force cancels an order"""
    from app.contexts.order.service import OrderService
    service = OrderService()
    
    return await service.cancel_order_from_event(
        db=db,
        order_id=order_id,
    )


# ============================================================
# PAYMENT ADMIN ROUTES
# ============================================================

@router.post("/payments/{payment_attempt_id}/fail")
async def admin_force_fail_payment(
    payment_attempt_id: int,
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin),
):
    """Admin force fails a payment"""
    from app.contexts.payment.service import PaymentService
    service = PaymentService()
    
    return await service.mark_payment_failed(
        db=db,
        payment_attempt_id=payment_attempt_id,
        failure_reason="Admin forced failure",
    )


# ============================================================
# REFUND ADMIN ROUTES
# ============================================================

@router.post("/refunds/force")
async def admin_force_refund(
    reservation_id: int,
    payment_attempt_id: int,
    amount: float,
    reason: str,
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin),
):
    """Admin force creates a refund request"""
    from app.contexts.refund.service import RefundService
    service = RefundService()
    
    return await service.create_refund_request(
        db=db,
        payment_attempt_id=payment_attempt_id,
        reservation_id=reservation_id,
        amount=amount,
        reason=reason,
        user_id=current_admin.id,
    )


@router.post("/refunds/{refund_request_id}/approve")
async def admin_approve_refund(
    refund_request_id: int,
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin),
):
    """Admin approves a refund request"""
    from app.contexts.refund.service import RefundService
    service = RefundService()
    
    return await service.approve_refund(
        db=db,
        refund_request_id=refund_request_id,
        user_id=current_admin.id,
    )


@router.post("/refunds/{refund_request_id}/reject")
async def admin_reject_refund(
    refund_request_id: int,
    rejection_reason: str,
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin),
):
    """Admin rejects a refund request"""
    from app.contexts.refund.service import RefundService
    service = RefundService()
    
    return await service.reject_refund(
        db=db,
        refund_request_id=refund_request_id,
        rejection_reason=rejection_reason,
        user_id=current_admin.id,
    )


# ============================================================
# SEAT ADMIN ROUTES
# ============================================================

@router.post("/seats/unlock")
async def admin_force_unlock_seat(
    showtime_id: int,
    seat_code: str,
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin),
):
    """Admin force unlocks a seat (for debugging stuck locks)"""
    from app.contexts.seat_availability.service import SeatAvailabilityService
    service = SeatAvailabilityService()
    
    return await service.unlock_seat(
        db=db,
        showtime_id=showtime_id,
        seat_code=seat_code,
    )


# ============================================================
# USER ADMIN ROUTES
# ============================================================

@router.get("/users/{user_id}/profile", response_model=UserProfileResponse)
def admin_get_user_profile(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin),
):
    """Admin views any user's profile"""
    from app.contexts.user.service import UserProfileService
    service = UserProfileService()
    
    return service.get_profile(db, user_id)


@router.patch("/users/{user_id}/type", response_model=UserProfileResponse)
async def admin_update_user_type(
    user_id: int,
    payload: AdminUpdateUserType,
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin),
):
    """Admin changes user's type (promote to admin / demote to user)"""
    from app.contexts.user.service import UserProfileService
    service = UserProfileService()
    
    return await service.admin_update_user_type(
        db=db,
        user_id=user_id,
        new_type=payload.user_type,
    )


@router.post("/users/{user_id}/deactivate")
async def admin_deactivate_user(
    user_id: int,
    reason: str,
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin),
):
    """Admin deactivates a user (bans them)"""
    from app.contexts.auth.repository import AuthRepository
    from app.core.errors import NotFoundError
    
    repo = AuthRepository()
    user = repo.get_user_by_id(db, user_id)
    
    if not user:
        raise NotFoundError("User not found")
    
    user.is_active = False
    repo.save(db, user)
    
    return {
        "user_id": user_id,
        "is_active": False,
        "reason": reason,
        "deactivated_by": current_admin.id,
    }


@router.delete("/users/{user_id}/profile", status_code=status.HTTP_204_NO_CONTENT)
async def admin_delete_user_profile(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin),
):
    """Admin deletes user profile"""
    from app.contexts.user.service import UserProfileService
    service = UserProfileService()
    
    await service.delete_profile(db, user_id)