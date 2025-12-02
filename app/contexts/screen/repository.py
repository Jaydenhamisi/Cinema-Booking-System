from app.shared.repositories.base import BaseRepository
from .models import Screen, SeatLayout

class ScreenRepository(BaseRepository):
    def __init__(self):
        super().__init__(Screen)

    def get_by_name(self, db, name: str):
        return db.query(Screen).filter(Screen.name == name).first()

class SeatLayoutRepository(BaseRepository):
    def __init__(self):
        super().__init__(SeatLayout)
