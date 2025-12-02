from datetime import datetime
from sqlalchemy import and_
from app.shared.repositories.base import BaseRepository

from .models import SeatLock, StatusEnum


class SeatLockRepository(BaseRepository):
    def __init__(self):
        super().__init__(SeatLock)

    def get_by_showtime_and_code(self, db, showtime_id, seat_code):
        return (
            db.query(SeatLock)
            .filter_by(showtime_id=showtime_id, seat_code=seat_code)
            .first()
        )

    def list_for_showtime(self, db, showtime_id):
        return db.query(SeatLock).filter_by(showtime_id=showtime_id).all()

    def get_expired(self, db, now: datetime):
        return (
            db.query(SeatLock)
            .filter(
                and_(
                    SeatLock.status == StatusEnum.LOCKED,
                    SeatLock.lock_expires_at != None,
                    SeatLock.lock_expires_at < now
                )
            )
            .all()
        )
