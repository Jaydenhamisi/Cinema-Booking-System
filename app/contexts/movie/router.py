# app/contexts/movie/router.py
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.errors import NotFoundError
from app.contexts.auth.dependencies import get_current_user  

from .service import MovieService  
from .schemas import (
    MovieCreate,
    MovieUpdate,
    MovieRead
)

router = APIRouter(
    prefix="/movies",
    tags=["movies"],
)


movie_service = MovieService()  


# CREATE MOVIE
@router.post("/", response_model=MovieRead)
async def create_movie_route(  
    payload: MovieCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),  
):
    return await movie_service.create_movie(  
        db=db, 
        data=payload,
        user_id=current_user.id
    )


# LIST MOVIES
@router.get("/", response_model=list[MovieRead])
def list_movies_route(
    db: Session = Depends(get_db),
):
    return movie_service.list_movies(db) 


# GET MOVIE BY ID
@router.get("/{movie_id}", response_model=MovieRead)
def get_movie_route(
    movie_id: int,
    db: Session = Depends(get_db),
):
    return movie_service.get_movie(db, movie_id)  


# UPDATE MOVIE
@router.put("/{movie_id}", response_model=MovieRead)
async def update_movie_route(  
    movie_id: int,
    payload: MovieUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),  
):
    return await movie_service.update_movie(  
        db=db,
        movie_id=movie_id,
        data=payload,
        user_id=current_user.id
    )


# DEACTIVATE MOVIE
@router.patch("/{movie_id}/deactivate", response_model=MovieRead)
async def deactivate_movie_route(  
    movie_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),  
):
    return await movie_service.deactivate_movie(  
        db=db,
        movie_id=movie_id,
        user_id=current_user.id
    )


# DELETE MOVIE
@router.delete("/{movie_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_movie_route(  
    movie_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),  
):
    await movie_service.delete_movie(  
        db=db,
        movie_id=movie_id,
        user_id=current_user.id
    )
    return None