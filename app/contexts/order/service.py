# app/contexts/order/service.py
from sqlalchemy.orm import Session

from app.core.errors import ValidationError, NotFoundError, ConflictError
from app.shared.services.event_publisher import publish_event_async

from .models import Order
from .repository import OrderRepository
from .events import (
    order_created_event,
    order_completed_event,
    order_cancelled_event,
    order_expired_event,
)


class OrderService:
    """Service for Order business logic."""
    
    def __init__(self):
        self.repo = OrderRepository()

    async def create_order_from_event(
        self, 
        db: Session, 
        user_id: int, 
        reservation_id: int,
        showtime_id: int,
        seat_code: str,
    ):
        """Create an order (triggered by reservation.created event)."""
        order = Order(
            user_id=user_id,
            reservation_id=reservation_id,
            pricing_snapshot={},
            final_amount=0,
            is_completed=False,
        )

        order = self.repo.create(db, order)

        event = order_created_event(
            order_id=order.id,
            reservation_id=reservation_id,
            user_id=user_id,
            showtime_id=showtime_id,
            seat_code=seat_code,
        )
        await publish_event_async(event["type"], event["payload"])

        return order

    async def complete_order_from_event(
        self,  
        db: Session,  
        order_id: int  
    ):
        """Complete an order (triggered by payment.succeeded event)."""
        order = self.repo.get_by_id(db, order_id)
        if order is None:
            raise NotFoundError("Order not found")

        if order.is_completed:
            raise ConflictError("Order already completed")
        
        order.is_completed = True

        order = self.repo.save(db, order)

        event = order_completed_event(order.id)
        await publish_event_async(event["type"], event["payload"])

        return order

    async def cancel_order_from_event(
        self,
        db: Session,
        order_id: int
    ):
        """Cancel an order (triggered by reservation.cancelled event)."""
        order = self.repo.get_by_id(db, order_id)
        if order is None:
            raise NotFoundError("Order not found")

        event = order_cancelled_event(order.id)
        await publish_event_async(event["type"], event["payload"])

        return order

    async def expire_order_from_event(
        self,
        db: Session,
        order_id: int
    ):
        """Expire an order (triggered by reservation.expired event)."""
        order = self.repo.get_by_id(db, order_id)
        if order is None:
            raise NotFoundError("Order not found")

        event = order_expired_event(order.id)
        await publish_event_async(event["type"], event["payload"])

        return order
    
    # ===== READ OPERATIONS (sync) =====
    
    def get_order(self, db: Session, order_id: int) -> Order:
        """Get order by ID."""
        order = self.repo.get_by_id(db, order_id)
        if not order:
            raise NotFoundError("Order not found")
        return order
    
    def list_user_orders(self, db: Session, user_id: int, completed_only: bool = False):
        """List orders for a user."""
        return self.repo.list_user_orders(db, user_id, completed_only=completed_only)