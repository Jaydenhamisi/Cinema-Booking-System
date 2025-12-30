from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import datetime, timezone

from app.core.errors import ValidationError, NotFoundError, ConflictError
from app.shared.services.event_publisher import publish_event_async  

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


class MovieService:
    """Service for Movie business logic."""
    
    def __init__(self):
        self.repo = MovieRepository()
    
    async def create_movie(self, db: Session, data: MovieCreate, user_id: int = None) -> Movie:
        """Create a new movie."""
        # Validation
        existing = self.repo.get_by_title(db, data.title)
        if existing is not None:
            raise ConflictError("Title already exists.")
        
        if data.duration_minutes <= 0:
            raise ValidationError("Duration must be greater than 0")
        
        # Create movie
        movie = Movie(
            title=data.title,
            description=data.description,
            duration_minutes=data.duration_minutes,
            release_date=data.release_date,
            age_rating=data.age_rating,
            poster_url=data.poster_url,
            trailer_url=data.trailer_url,
        )

        movie = self.repo.create(db, movie)

        # Emit event
        event = movie_created_event(movie.id, user_id=user_id)
        await publish_event_async(event["type"], event["payload"])

        return movie

    async def update_movie(self, db: Session, movie_id: int, data: MovieUpdate, user_id: int = None) -> Movie:
        """Update an existing movie."""
        movie = self.repo.get_by_id(db, movie_id)
        if movie is None:
            raise NotFoundError("Movie not found")

        # Validation
        if data.duration_minutes is not None and data.duration_minutes <= 0:
            raise ValidationError("Duration must be greater than 0")
        
        if data.title is not None:
            existing = self.repo.get_by_title(db, data.title)
            if existing and existing.id != movie_id:
                raise ConflictError("Title already exists.")

        # Update fields
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(movie, key, value)

        movie = self.repo.save(db, movie)

        # Emit event
        event = movie_updated_event(movie.id, user_id=user_id)
        await publish_event_async(event["type"], event["payload"])

        return movie

    async def deactivate_movie(self, db: Session, movie_id: int, user_id: int = None) -> Movie:
        """Deactivate a movie (soft delete)."""
        movie = self.repo.get_by_id(db, movie_id)
        if movie is None:
            raise NotFoundError("Movie not found")
        
        movie.is_active = False
        movie = self.repo.save(db, movie)

        # Emit event
        event = movie_deactivated_event(movie.id, user_id=user_id)
        await publish_event_async(event["type"], event["payload"])

        return movie

    async def delete_movie(self, db: Session, movie_id: int, user_id: int = None) -> int:
        """Delete a movie (hard delete)."""
        movie = self.repo.get_by_id(db, movie_id)
        if movie is None:
            raise NotFoundError("Movie not found")
        
        # Check for future showtimes
        now = datetime.now(timezone.utc)
        future_showtimes = db.scalars(
            select(Showtime).where(
                Showtime.movie_id == movie_id,
                Showtime.start_time > now
            )
        ).first()

        if future_showtimes is not None:
            raise ConflictError("Movie has future showtimes. Deactivate instead")
        
        self.repo.delete(db, movie)

        # Emit event
        event = movie_deleted_event(movie_id, user_id=user_id)
        await publish_event_async(event["type"], event["payload"])

        return movie_id
    
    def get_movie(self, db: Session, movie_id: int) -> Movie:
        """Get movie by ID (read operation, can stay sync)."""
        movie = self.repo.get_by_id(db, movie_id)
        if not movie:
            raise NotFoundError("Movie not found")
        return movie
    
    def list_movies(self, db: Session, active_only: bool = True):
        """List all movies (read operation, can stay sync)."""
        return self.repo.list_all(db, active_only=active_only)