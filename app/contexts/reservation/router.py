# app/contexts/reservation/router.py
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.errors import NotFoundError
from ..auth.dependencies import get_current_user  
from .service import ReservationService
from .schemas import (
    ReservationCreate,
    ReservationRead,
)

router = APIRouter(
    prefix="/reservations",
    tags=["reservations"],
)

# Create service instance
reservation_service = ReservationService()


@router.post("/", response_model=ReservationRead)
async def create_reservation_route(
    payload: ReservationCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),  
):
    return await reservation_service.create_reservation(
        db=db, 
        user_id=current_user.id, 
        data=payload
    )


@router.get("/", response_model=list[ReservationRead])
def list_reservations_route(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user), 
):
    return reservation_service.list_user_reservations(db, current_user.id)


@router.get("/{reservation_id}", response_model=ReservationRead)
def get_reservation_route(
    reservation_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),  
):
    reservation = reservation_service.get_reservation(db, reservation_id)
    
    # Check ownership
    if reservation.user_id != current_user.id:
        raise NotFoundError("Reservation not found")  # Don't leak existence
    
    return reservation


@router.post("/{reservation_id}/cancel", response_model=ReservationRead)
async def cancel_reservation_route(
    reservation_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),  
):
    return await reservation_service.cancel_reservation(
        db=db, 
        reservation_id=reservation_id, 
        user_id=current_user.id
    )