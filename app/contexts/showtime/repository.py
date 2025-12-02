from sqlalchemy.orm import Session
from sqlalchemy import select
from app.shared.repositories.base import BaseRepository
from .models import Showtime


class ShowtimeRepository(BaseRepository):
    def __init__(self):
        super().__init__(Showtime)

    def get(self, db: Session, showtime_id: int):
        return db.get(Showtime, showtime_id)

    def list_all(self, db: Session):
        return db.scalars(select(Showtime)).all()

    def list_for_movie(self, db: Session, movie_id: int):
        return db.scalars(
            select(Showtime).where(Showtime.movie_id == movie_id)
        ).all()

    def list_for_screen(self, db: Session, screen_id: int):
        return db.scalars(
            select(Showtime).where(Showtime.screen_id == screen_id)
        ).all()

    def find_overlap(self, db: Session, screen_id, start_time, end_time, exclude_id=None):
        stmt = select(Showtime).where(
            Showtime.screen_id == screen_id,
            Showtime.start_time < end_time,
            Showtime.end_time > start_time,
            Showtime.is_active == True,
        )

        if exclude_id:
            stmt = stmt.where(Showtime.id != exclude_id)

        return db.scalar(stmt)

    def delete(self, db: Session, showtime: Showtime):
        db.delete(showtime)
        db.commit()
