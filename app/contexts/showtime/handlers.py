# app/contexts/showtime/handlers.py

"""
ShowtimeContext inbound event handlers.

Listens to:
- screen.deleted
- movie.deactivated
- admin.force_cancel_showtime
"""

from datetime import datetime, timezone
from sqlalchemy import select

from app.core.event_bus import event_bus
from app.core.database import SessionLocal
from .models import Showtime


def _utcnow():
    return datetime.now(timezone.utc)


# -----------------------------------------------------------
# EVENT 1: screen.deleted → cancel future showtimes
# -----------------------------------------------------------
async def on_screen_deleted(payload: dict):
    screen_id = payload.get("screen_id")
    if screen_id is None:
        return

    db = SessionLocal()
    try:
        now = _utcnow()
        showtimes = db.scalars(
            select(Showtime).where(
                Showtime.screen_id == screen_id,
                Showtime.start_time >= now,
                Showtime.is_active == True,
            )
        ).all()

        for st in showtimes:
            st.is_active = False

        db.commit()
    finally:
        db.close()


event_bus.subscribe("screen.deleted", on_screen_deleted)


# -----------------------------------------------------------
# EVENT 2: movie.deactivated → cancel future showtimes
# -----------------------------------------------------------
async def on_movie_deactivated(payload: dict):
    movie_id = payload.get("movie_id")
    if movie_id is None:
        return

    db = SessionLocal()
    try:
        now = _utcnow()
        showtimes = db.scalars(
            select(Showtime).where(
                Showtime.movie_id == movie_id,
                Showtime.start_time >= now,
                Showtime.is_active == True,
            )
        ).all()

        for st in showtimes:
            st.is_active = False

        db.commit()
    finally:
        db.close()


event_bus.subscribe("movie.deactivated", on_movie_deactivated)


# -----------------------------------------------------------
# EVENT 3: admin.force_cancel_showtime → cancel one showtime
# -----------------------------------------------------------
async def on_admin_force_cancel_showtime(payload: dict):
    showtime_id = payload.get("showtime_id")
    if showtime_id is None:
        return

    db = SessionLocal()
    try:
        st = db.get(Showtime, showtime_id)
        if not st:
            return

        if st.is_active:
            st.is_active = False
            db.commit()
    finally:
        db.close()


event_bus.subscribe("admin.force_cancel_showtime", on_admin_force_cancel_showtime)
