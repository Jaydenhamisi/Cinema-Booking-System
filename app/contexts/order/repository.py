# app/contexts/order/repository.py

from sqlalchemy.orm import Session
from sqlalchemy import select
from .models import Order



class OrderRepository:

    def get_order_by_id(self, db: Session, order_id: int):
        return db.get(Order, order_id)
    

    def list_orders(self, db: Session, user_id:int, completed_only: bool = True):
        stmt = select(Order).where(Order.user_id == user_id)
        if completed_only:
            stmt = stmt.where(Order.is_completed == True)
        return db.scalars(stmt).all()
    
    
    def create(self, db: Session, order: Order):
        db.add(order)
        db.commit()
        db.refresh(order)
        return order
    
    def save(self, db: Session, order: Order):
        db.add(order)
        db.commit()
        db.refresh(order)
        return order
    
    def get_user_order_by_id(self, db: Session, order_id: int, user_id: int):
        stmt = select(Order).where(
            Order.id == order_id,
            Order.user_id == user_id
        )
        return db.scalar(stmt)

    
    def list_user_orders(self, db, user_id, completed_only=True):
        stmt = (
            select(Order)
            .where(Order.user_id == user_id)
            .order_by(Order.created_at.desc())
        )

        if completed_only:
            stmt = stmt.where(Order.is_completed == True)

        return db.scalars(stmt).all()
    

    def get_order_by_reservation_id(self, db, reservation_id):
        stmt = select(Order).where(Order.reservation_id == reservation_id)
        
        return db.scalar(stmt)



