from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.errors import NotFoundError

from .repository import MovieRepository
from .service import (
    create_movie,
    update_movie,
    deactivate_movie,
    delete_movie
)
from .schemas import (
    MovieCreate,
    MovieUpdate,
    MovieRead
)

repo = MovieRepository()

router = APIRouter(
    prefix="/movies",
    tags=["movies"],
)


# CREATE MOVIE
@router.post("/", response_model=MovieRead)
def create_movie_route(
    payload: MovieCreate,
    db: Session = Depends(get_db),
):
    return create_movie(db=db, data=payload)


# LIST MOVIES
@router.get("/", response_model=list[MovieRead])
def list_movies_route(
    db: Session = Depends(get_db),
):
    return repo.list_all(db)


# GET MOVIE BY ID
@router.get("/{movie_id}", response_model=MovieRead)
def get_movie_route(
    movie_id: int,
    db: Session = Depends(get_db),
):
    movie = repo.get_by_id(db, movie_id)
    if movie is None:
        raise NotFoundError("Movie not found")
    return movie


# UPDATE MOVIE
@router.put("/{movie_id}", response_model=MovieRead)
def update_movie_route(
    movie_id: int,
    payload: MovieUpdate,
    db: Session = Depends(get_db),
):
    return update_movie(db=db, movie_id=movie_id, data=payload)


# DEACTIVATE MOVIE
@router.patch("/{movie_id}/deactivate", response_model=MovieRead)
def deactivate_movie_route(
    movie_id: int,
    db: Session = Depends(get_db),
):
    return deactivate_movie(db=db, movie_id=movie_id)


# DELETE MOVIE
@router.delete("/{movie_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_movie_route(
    movie_id: int,
    db: Session = Depends(get_db),
):
    delete_movie(db=db, movie_id=movie_id)
    return None
