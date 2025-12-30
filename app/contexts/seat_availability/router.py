# app/contexts/seat_availability/router.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.contexts.auth.dependencies import get_current_user

from .service import SeatAvailabilityService
from .schemas import (
    SeatLockCreate,
    SeatLockResponse,
    SeatAvailabilityGridResponse,
)

router = APIRouter(
    prefix="/seatavailability",
    tags=["seatavailability"],
)

# Create service instance
seat_service = SeatAvailabilityService()


@router.post("/lock", response_model=SeatLockResponse)
async def lock_seat_route(
    payload: SeatLockCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),  # Added auth
):
    """Lock a seat for the authenticated user."""
    return await seat_service.lock_seat(
        db=db,
        showtime_id=payload.showtime_id,
        seat_code=payload.seat_code,
        user_id=current_user.id,  # Use authenticated user
    )


@router.post("/unlock", response_model=SeatLockResponse)
async def unlock_seat_route(
    payload: SeatLockCreate,
    db: Session = Depends(get_db),
):
    """Unlock a seat (system/admin-triggered via events)."""
    return await seat_service.unlock_seat(
        db=db,
        showtime_id=payload.showtime_id,
        seat_code=payload.seat_code,
    )


@router.get("/grid/{showtime_id}", response_model=SeatAvailabilityGridResponse)
def grid_route(
    showtime_id: int,
    db: Session = Depends(get_db),
):
    """Return seat availability grid for a showtime."""
    seats = seat_service.get_availability_grid(db, showtime_id=showtime_id)
    return {"showtime_id": showtime_id, "seats": seats}