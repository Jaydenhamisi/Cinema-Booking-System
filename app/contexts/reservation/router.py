from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.errors import NotFoundError
from ..auth.dependencies import get_current_user  
from .service import (
    create_reservation,
    cancel_reservation,
)
from .schemas import (
    ReservationCreate,
    ReservationRead,
)
from .repository import ReservationRepository

repo = ReservationRepository()

router = APIRouter(
    prefix="/reservations",
    tags=["reservations"],
)


@router.post("/", response_model=ReservationRead)
def create_reservation_route(
    payload: ReservationCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),  
):
    return create_reservation(db=db, user_id=current_user.id, data=payload)  


@router.get("/", response_model=list[ReservationRead])
def list_reservations_route(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user), 
):
    return repo.list_for_user(db, current_user.id)  


@router.get("/{reservation_id}", response_model=ReservationRead)
def get_reservation_route(
    reservation_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),  
):
    reservation = repo.get_by_id(db, reservation_id)
    if reservation is None:
        raise NotFoundError("Reservation not found")
    
    # Optional: Check ownership
    if reservation.user_id != current_user.id:
        raise NotFoundError("Reservation not found")  # Don't leak existence
    
    return reservation


@router.post("/{reservation_id}/cancel", response_model=ReservationRead)
def cancel_reservation_route(
    reservation_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),  
):
    return cancel_reservation(db=db, reservation_id=reservation_id, user_id=current_user.id)