# app/contexts/movie/service.py

from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import datetime, timezone

from app.core.errors import ValidationError, NotFoundError, ConflictError
from app.shared.services.event_publisher import publish_event

from .models import Movie
from app.contexts.showtime.models import Showtime
from .schemas import MovieCreate, MovieUpdate
from .repository import MovieRepository
from .events import (
    movie_created_event,
    movie_updated_event,
    movie_deactivated_event,
    movie_deleted_event
)

repo = MovieRepository()


def create_movie(db: Session, data: MovieCreate) -> Movie:
    existing = repo.get_by_title(db, data.title)
    if existing is not None:
        raise ConflictError ("Title already exists.")
    
    if data.duration_minutes <= 0:
        raise ValidationError ("Duration must be greater than 0")
    
    movie = Movie(
        title=data.title,
        description=data.description,
        duration_minutes=data.duration_minutes,
        release_date=data.release_date,
        age_rating=data.age_rating,
        poster_url=data.poster_url,
        trailer_url=data.trailer_url,
    )

    repo.create(db, movie)

    event = movie_created_event(movie.id)
    publish_event(event["type"], event["payload"])

    return movie


def update_movie(db: Session, movie_id: int, data: MovieUpdate) -> Movie:
    movie = repo.get_by_id(db, movie_id)
    if movie is None:
        raise NotFoundError("Movie not found")

    if data.duration_minutes is not None and data.duration_minutes <= 0:
        raise ValidationError("Duration must be greater than 0")
    
    if data.title is not None:
        existing = repo.get_by_title(db, data.title)
        if existing and existing.id != movie_id:
            raise ConflictError("Title already exists.")


    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(movie, key, value)

    db.commit()

    event = movie_updated_event(movie.id)
    publish_event(event["type"], event["payload"])

    return movie


def deactivate_movie(db: Session, movie_id: int) -> Movie:
    movie = repo.get_by_id(db, movie_id)
    if movie is None:
        raise NotFoundError("Movie not found")
    
    movie.is_active = False

    db.commit()

    event = movie_deactivated_event(movie.id)
    publish_event(event["type"], event["payload"])

    return movie

    

def delete_movie(db: Session, movie_id: int) -> int:
    movie = repo.get_by_id(db, movie_id)
    if movie is None:
        raise NotFoundError("Movie not found")
    
    now = datetime.now(timezone.utc)
    future_showtimes = db.scalars(
        select(Showtime).where(
            Showtime.movie_id == movie_id,
            Showtime.start_time > now
        )
    ).first()

    if future_showtimes is not None:
        raise ConflictError("Movie has future showtimes. Deactivate instead")
    

    repo.delete(db, movie)

    event = movie_deleted_event(movie_id)
    publish_event(event["type"], event["payload"])

    return movie_id