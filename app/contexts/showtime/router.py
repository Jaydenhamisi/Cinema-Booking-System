# app/contexts/showtime/router.py
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.contexts.auth.dependencies import get_current_user
from .service import ShowtimeService
from .schemas import ShowtimeCreate, ShowtimeUpdate, ShowtimeRead

router = APIRouter(
    prefix="/showtimes",
    tags=["showtimes"],
)

# Create service instance
showtime_service = ShowtimeService()


@router.post("/", response_model=ShowtimeRead, status_code=status.HTTP_201_CREATED)
async def create_showtime_route(
    payload: ShowtimeCreate, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    return await showtime_service.create_showtime(db, payload, user_id=current_user.id)


@router.get("/", response_model=list[ShowtimeRead])
def list_showtimes_route(db: Session = Depends(get_db)):
    return showtime_service.list_showtimes(db)


@router.get("/{showtime_id}", response_model=ShowtimeRead)
def get_showtime_route(showtime_id: int, db: Session = Depends(get_db)):
    return showtime_service.get_showtime(db, showtime_id)


@router.get("/movie/{movie_id}", response_model=list[ShowtimeRead])
def list_showtimes_for_movie_route(movie_id: int, db: Session = Depends(get_db)):
    return showtime_service.list_showtimes_for_movie(db, movie_id)


@router.get("/screen/{screen_id}", response_model=list[ShowtimeRead])
def list_showtimes_for_screen_route(screen_id: int, db: Session = Depends(get_db)):
    return showtime_service.list_showtimes_for_screen(db, screen_id)


@router.put("/{showtime_id}", response_model=ShowtimeRead)
async def update_showtime_route(
    showtime_id: int,
    payload: ShowtimeUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    return await showtime_service.update_showtime(db, showtime_id, payload, user_id=current_user.id)


@router.delete("/{showtime_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_showtime_route(
    showtime_id: int, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    await showtime_service.delete_showtime(db, showtime_id, user_id=current_user.id)
    return None