# app/contexts/reservation/repository.py
from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session
from sqlalchemy import select

from .models import Reservation, ReservationStatus


class ReservationRepository:
    """Repository for Reservation aggregate."""

    def get_by_id(self, db: Session, reservation_id: int) -> Optional[Reservation]:
        """Get reservation by ID."""
        return db.get(Reservation, reservation_id)

    def list_for_user(self, db: Session, user_id: int) -> List[Reservation]:
        """List all reservations for a user."""
        stmt = (
            select(Reservation)
            .where(Reservation.user_id == user_id)
            .order_by(Reservation.created_at.desc())
        )
        return db.scalars(stmt).all()

    def list_active_for_showtime(self, db: Session, showtime_id: int) -> List[Reservation]:
        """List active reservations for a showtime."""
        stmt = select(Reservation).where(
            Reservation.showtime_id == showtime_id,
            Reservation.status == ReservationStatus.ACTIVE,
        )
        return db.scalars(stmt).all()

    def get_active_by_showtime_and_seat(
        self,
        db: Session,
        showtime_id: int,
        seat_code: str,
    ) -> Optional[Reservation]:
        """Get active reservation for a specific seat at a showtime."""
        stmt = select(Reservation).where(
            Reservation.showtime_id == showtime_id,
            Reservation.seat_code == seat_code,
            Reservation.status == ReservationStatus.ACTIVE,
        )
        return db.scalars(stmt).first()

    def get_expired(self, db: Session, now: datetime) -> List[Reservation]:
        """Get all expired reservations that need cleanup."""
        stmt = select(Reservation).where(
            Reservation.status == ReservationStatus.ACTIVE,
            Reservation.expires_at.is_not(None),
            Reservation.expires_at <= now,
        )
        return db.scalars(stmt).all()

    def create(self, db: Session, reservation: Reservation) -> Reservation:
        """Create a new reservation."""
        db.add(reservation)
        db.commit()
        db.refresh(reservation)
        return reservation

    def save(self, db: Session, reservation: Reservation) -> Reservation:
        """Update existing reservation."""
        db.add(reservation)
        db.commit()
        db.refresh(reservation)
        return reservation