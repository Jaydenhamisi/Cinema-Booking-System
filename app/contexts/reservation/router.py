from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.errors import NotFoundError
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
):
    # user_id will come from auth when we wire it; hard-code or pass later
    user_id = 1  # placeholder for now
    return create_reservation(db=db, user_id=user_id, data=payload)


@router.get("/", response_model=list[ReservationRead])
def list_reservations_route(
    db: Session = Depends(get_db),
):
    # later will filter by current_user
    # for now return all for simplicity
    # can switch this to repo.list_for_user(db, current_user.id)
    stmt = repo.list_for_user  # type: ignore  # you'll actually call it properly or change this
    return []  # placeholder if you want to fill later


@router.get("/{reservation_id}", response_model=ReservationRead)
def get_reservation_route(
    reservation_id: int,
    db: Session = Depends(get_db),
):
    reservation = repo.get_by_id(db, reservation_id)
    if reservation is None:
        raise NotFoundError("Reservation not found")
    return reservation


@router.post("/{reservation_id}/cancel", response_model=ReservationRead)
def cancel_reservation_route(
    reservation_id: int,
    db: Session = Depends(get_db),
):
    # user_id comes from auth later
    return cancel_reservation(db=db, reservation_id=reservation_id)
