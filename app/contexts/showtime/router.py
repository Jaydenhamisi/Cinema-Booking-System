# app/contexts/showtime/router.py

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from .service import (
    create_showtime,
    list_showtimes,
    get_showtime,
    list_showtimes_for_movie,
    list_showtimes_for_screen,
    update_showtime,
    delete_showtime,
)
from .schemas import ShowtimeCreate, ShowtimeUpdate, ShowtimeRead

router = APIRouter(
    prefix="/showtimes",
    tags=["showtimes"],
)


@router.post("/", response_model=ShowtimeRead, status_code=status.HTTP_201_CREATED)
def create_showtime_route(payload: ShowtimeCreate, db: Session = Depends(get_db)):
    return create_showtime(db=db, data=payload)


@router.get("/", response_model=list[ShowtimeRead])
def list_showtimes_route(db: Session = Depends(get_db)):
    return list_showtimes(db=db)


@router.get("/{showtime_id}", response_model=ShowtimeRead)
def get_showtime_route(showtime_id: int, db: Session = Depends(get_db)):
    return get_showtime(db=db, showtime_id=showtime_id)


@router.get("/movie/{movie_id}", response_model=list[ShowtimeRead])
def list_showtimes_for_movie_route(movie_id: int, db: Session = Depends(get_db)):
    return list_showtimes_for_movie(db=db, movie_id=movie_id)


@router.get("/screen/{screen_id}", response_model=list[ShowtimeRead])
def list_showtimes_for_screen_route(screen_id: int, db: Session = Depends(get_db)):
    return list_showtimes_for_screen(db=db, screen_id=screen_id)


@router.put("/{showtime_id}", response_model=ShowtimeRead)
def update_showtime_route(
    showtime_id: int,
    payload: ShowtimeUpdate,
    db: Session = Depends(get_db),
):
    return update_showtime(db=db, showtime_id=showtime_id, data=payload)


@router.delete("/{showtime_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_showtime_route(showtime_id: int, db: Session = Depends(get_db)):
    delete_showtime(db=db, showtime_id=showtime_id)
    return None
