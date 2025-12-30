# app/contexts/screen/repository.py
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from .models import Screen, SeatLayout


class ScreenRepository:
    """Repository for Screen aggregate."""

    def get_by_id(self, db: Session, screen_id: int):
        """Get screen by ID."""
        return db.get(Screen, screen_id)

    def get_by_name(self, db: Session, name: str):
        """Get screen by name."""
        return db.query(Screen).filter(Screen.name == name).first()

    def list_all(self, db: Session):
        """List all screens."""
        return db.scalars(select(Screen)).all()

    def create(self, db: Session, screen: Screen):
        """Create a new screen."""
        db.add(screen)
        db.commit()
        db.refresh(screen)
        return screen

    def save(self, db: Session, screen: Screen):
        """Update existing screen."""
        db.add(screen)
        db.commit()
        db.refresh(screen)
        return screen

    def delete(self, db: Session, screen: Screen):
        """Delete a screen."""
        db.delete(screen)
        db.commit()

    def count_screens_using_layout(self, db: Session, layout_id: int) -> int:
        """Count how many screens use a specific layout."""
        return db.scalar(
            select(func.count())
            .select_from(Screen)
            .where(Screen.seat_layout_id == layout_id)
        )


class SeatLayoutRepository:
    """Repository for SeatLayout aggregate."""

    def get_by_id(self, db: Session, layout_id: int):
        """Get layout by ID."""
        return db.get(SeatLayout, layout_id)

    def get_by_name(self, db: Session, name: str):
        """Get layout by name."""
        return db.scalar(
            select(SeatLayout).where(SeatLayout.name == name)
        )

    def list_all(self, db: Session):
        """List all layouts."""
        return db.scalars(select(SeatLayout)).all()

    def create(self, db: Session, layout: SeatLayout):
        """Create a new layout."""
        db.add(layout)
        db.commit()
        db.refresh(layout)
        return layout

    def save(self, db: Session, layout: SeatLayout):
        """Update existing layout."""
        db.add(layout)
        db.commit()
        db.refresh(layout)
        return layout

    def delete(self, db: Session, layout: SeatLayout):
        """Delete a layout."""
        db.delete(layout)
        db.commit()