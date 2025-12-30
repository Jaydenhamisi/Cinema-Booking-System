# app/contexts/order/repository.py
from sqlalchemy.orm import Session
from sqlalchemy import select
from .models import Order


class OrderRepository:
    """Repository for Order aggregate."""

    def get_by_id(self, db: Session, order_id: int):
        """Get order by ID."""
        return db.get(Order, order_id)
    
    def get_by_reservation_id(self, db: Session, reservation_id: int):
        """Get order by reservation ID."""
        stmt = select(Order).where(Order.reservation_id == reservation_id)
        return db.scalar(stmt)

    def list_user_orders(self, db: Session, user_id: int, completed_only: bool = True):
        """List orders for a user."""
        stmt = (
            select(Order)
            .where(Order.user_id == user_id)
            .order_by(Order.created_at.desc())
        )

        if completed_only:
            stmt = stmt.where(Order.is_completed == True)

        return db.scalars(stmt).all()
    
    def create(self, db: Session, order: Order):
        """Create a new order."""
        db.add(order)
        db.commit()
        db.refresh(order)
        return order
    
    def save(self, db: Session, order: Order):
        """Update existing order."""
        db.add(order)
        db.commit()
        db.refresh(order)
        return order