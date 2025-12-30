# app/contexts/showtime/service.py
from sqlalchemy.orm import Session

from app.core.errors import ValidationError, NotFoundError, ConflictError
from app.shared.services.event_publisher import publish_event_async

from .models import Showtime
from .schemas import ShowtimeCreate, ShowtimeUpdate
from .events import (
    showtime_created_event,
    showtime_updated_event,
    showtime_deleted_event,
    showtime_cancelled_event
)

from app.contexts.movie.models import Movie
from app.contexts.screen.models import Screen
from .repository import ShowtimeRepository


class ShowtimeService:
    """Service for Showtime business logic."""
    
    def __init__(self):
        self.repo = ShowtimeRepository()

    # =====================================================================
    # CREATE
    # =====================================================================
    
    async def create_showtime(
        self, 
        db: Session, 
        data: ShowtimeCreate, 
        user_id: int = None
    ) -> Showtime:
        """Create a new showtime."""
        # Movie must exist + active
        movie = db.get(Movie, data.movie_id)
        if not movie or not movie.is_active:
            raise NotFoundError(
                "Movie not found or inactive", 
                context={"movie_id": data.movie_id}
            )

        # Screen must exist
        screen = db.get(Screen, data.screen_id)
        if not screen:
            raise NotFoundError(
                "Screen not found", 
                context={"screen_id": data.screen_id}
            )

        # Time rule
        if data.end_time <= data.start_time:
            raise ValidationError("end_time must be after start_time")

        # Overlap invariant
        conflict = self.repo.find_overlap(
            db,
            screen_id=data.screen_id,
            start_time=data.start_time,
            end_time=data.end_time,
        )

        if conflict:
            raise ConflictError(
                "Screen already has a showtime during this time window",
                context={"screen_id": data.screen_id},
            )

        # Create showtime
        showtime = Showtime(
            start_time=data.start_time,
            end_time=data.end_time,
            format=data.format,
            movie_id=data.movie_id,
            screen_id=data.screen_id,
        )

        showtime = self.repo.create(db, showtime)

        # Emit event
        event = showtime_created_event(showtime.id, user_id=user_id)
        await publish_event_async(event["type"], event["payload"])

        return showtime

    # =====================================================================
    # READ
    # =====================================================================
    
    def get_showtime(self, db: Session, showtime_id: int) -> Showtime:
        """Get showtime by ID (read operation, stays sync)."""
        showtime = self.repo.get_by_id(db, showtime_id)
        if not showtime:
            raise NotFoundError(
                "Showtime not found", 
                context={"showtime_id": showtime_id}
            )
        return showtime

    def list_showtimes(self, db: Session):
        """List all showtimes (read operation, stays sync)."""
        return self.repo.list_all(db)

    def list_showtimes_for_movie(self, db: Session, movie_id: int):
        """List showtimes for a movie (read operation, stays sync)."""
        return self.repo.list_for_movie(db, movie_id)

    def list_showtimes_for_screen(self, db: Session, screen_id: int):
        """List showtimes for a screen (read operation, stays sync)."""
        return self.repo.list_for_screen(db, screen_id)

    # =====================================================================
    # UPDATE
    # =====================================================================
    
    async def update_showtime(
        self, 
        db: Session, 
        showtime_id: int, 
        data: ShowtimeUpdate, 
        user_id: int = None
    ) -> Showtime:
        """Update an existing showtime."""
        showtime = self.repo.get_by_id(db, showtime_id)
        if not showtime:
            raise NotFoundError(
                "Showtime not found", 
                context={"showtime_id": showtime_id}
            )

        updates = data.model_dump(exclude_unset=True)

        # Validate movie reference if changing
        if "movie_id" in updates:
            movie = db.get(Movie, updates["movie_id"])
            if not movie or not movie.is_active:
                raise NotFoundError(
                    "Movie not found or inactive",
                    context={"movie_id": updates["movie_id"]},
                )

        # Validate screen reference if changing
        if "screen_id" in updates:
            screen = db.get(Screen, updates["screen_id"])
            if not screen:
                raise NotFoundError(
                    "Screen not found", 
                    context={"screen_id": updates["screen_id"]}
                )

        # Apply updates
        for field, value in updates.items():
            setattr(showtime, field, value)

        # Time invariant
        if showtime.end_time <= showtime.start_time:
            raise ValidationError("end_time must be after start_time")

        # Overlap check
        conflict = self.repo.find_overlap(
            db,
            screen_id=showtime.screen_id,
            start_time=showtime.start_time,
            end_time=showtime.end_time,
            exclude_id=showtime.id,
        )

        if conflict:
            raise ConflictError(
                "Updated time window conflicts with another showtime",
                context={"showtime_id": showtime_id},
            )

        showtime = self.repo.save(db, showtime)

        # Emit event
        event = showtime_updated_event(showtime.id, user_id=user_id)
        await publish_event_async(event["type"], event["payload"])

        return showtime

    # =====================================================================
    # DELETE
    # =====================================================================
    
    async def delete_showtime(
        self, 
        db: Session, 
        showtime_id: int, 
        user_id: int = None
    ) -> None:
        """Delete a showtime."""
        showtime = self.repo.get_by_id(db, showtime_id)
        if not showtime:
            raise NotFoundError(
                "Showtime not found", 
                context={"showtime_id": showtime_id}
            )

        self.repo.delete(db, showtime)

        # Emit event
        event = showtime_deleted_event(showtime_id, user_id=user_id)
        await publish_event_async(event["type"], event["payload"])

    async def cancel_showtime(
        self, 
        db: Session, 
        showtime_id: int, 
        reason: str = None,
        user_id: int = None
    ) -> Showtime:
        """Cancel a showtime (soft delete)."""
        showtime = self.repo.get_by_id(db, showtime_id)
        if not showtime:
            raise NotFoundError(
                "Showtime not found", 
                context={"showtime_id": showtime_id}
            )
        
        if not showtime.is_active:
            return showtime  # Already cancelled, idempotent
        
        showtime.is_active = False
        showtime = self.repo.save(db, showtime)
        
        # Emit event
        event = showtime_cancelled_event(showtime_id, reason=reason, user_id=user_id)
        await publish_event_async(event["type"], event["payload"])
        
        return showtime