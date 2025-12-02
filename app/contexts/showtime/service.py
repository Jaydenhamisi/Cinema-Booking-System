# app/contexts/showtime/service.py

from sqlalchemy.orm import Session

from app.core.errors import ValidationError, NotFoundError, ConflictError
from app.shared.services.event_publisher import publish_event

from .models import Showtime
from .schemas import ShowtimeCreate, ShowtimeUpdate
from .events import (
    showtime_created_event,
    showtime_updated_event,
    showtime_deleted_event,
)

from app.contexts.movie.models import Movie
from app.contexts.screen.models import Screen
from .repository import ShowtimeRepository

repo = ShowtimeRepository()


# =====================================================================
# CREATE
# =====================================================================
def create_showtime(db: Session, data: ShowtimeCreate) -> Showtime:
    # Movie must exist + active
    movie = db.get(Movie, data.movie_id)
    if not movie or not movie.is_active:
        raise NotFoundError("Movie not found or inactive", context={"movie_id": data.movie_id})

    # Screen must exist
    screen = db.get(Screen, data.screen_id)
    if not screen:
        raise NotFoundError("Screen not found", context={"screen_id": data.screen_id})

    # Time rule
    if data.end_time <= data.start_time:
        raise ValidationError("end_time must be after start_time")

    # Overlap invariant (via repository)
    conflict = repo.find_overlap(
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

    db.add(showtime)
    db.commit()
    db.refresh(showtime)

    event = showtime_created_event(showtime.id)
    publish_event(event["type"], event["payload"])

    return showtime


# =====================================================================
# READ
# =====================================================================
def get_showtime(db: Session, showtime_id: int) -> Showtime:
    showtime = repo.get(db, showtime_id)
    if not showtime:
        raise NotFoundError("Showtime not found", context={"showtime_id": showtime_id})
    return showtime


def list_showtimes(db: Session):
    return repo.list_all(db)


def list_showtimes_for_movie(db: Session, movie_id: int):
    return repo.list_for_movie(db, movie_id)


def list_showtimes_for_screen(db: Session, screen_id: int):
    return repo.list_for_screen(db, screen_id)


# =====================================================================
# UPDATE
# =====================================================================
def update_showtime(db: Session, showtime_id: int, data: ShowtimeUpdate) -> Showtime:
    showtime = repo.get(db, showtime_id)
    if not showtime:
        raise NotFoundError("Showtime not found", context={"showtime_id": showtime_id})

    updates = data.model_dump(exclude_unset=True)

    # Validate movie reference
    if "movie_id" in updates:
        movie = db.get(Movie, updates["movie_id"])
        if not movie or not movie.is_active:
            raise NotFoundError(
                "Movie not found or inactive",
                context={"movie_id": updates["movie_id"]},
            )

    # Validate screen reference
    if "screen_id" in updates:
        screen = db.get(Screen, updates["screen_id"])
        if not screen:
            raise NotFoundError("Screen not found", context={"screen_id": updates["screen_id"]})

    # Tentatively apply
    for field, value in updates.items():
        setattr(showtime, field, value)

    # Time invariant
    if showtime.end_time <= showtime.start_time:
        raise ValidationError("end_time must be after start_time")

    # Overlap check (via repo)
    conflict = repo.find_overlap(
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

    db.commit()
    db.refresh(showtime)

    event = showtime_updated_event(showtime.id)
    publish_event(event["type"], event["payload"])

    return showtime


# =====================================================================
# DELETE
# =====================================================================
def delete_showtime(db: Session, showtime_id: int) -> None:
    showtime = repo.get(db, showtime_id)
    if not showtime:
        raise NotFoundError("Showtime not found", context={"showtime_id": showtime_id})

    repo.delete(db, showtime)

    event = showtime_deleted_event(showtime_id)
    publish_event(event["type"], event["payload"])


