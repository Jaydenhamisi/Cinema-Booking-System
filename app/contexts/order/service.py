# app/contexts/order/service.py

from sqlalchemy.orm import Session

from app.core.errors import ValidationError, NotFoundError, ConflictError
from app.shared.services.event_publisher import publish_event_async  # Changed!

from .models import Order
from .repository import OrderRepository
from .events import (
    order_created_event,
    order_completed_event,
    order_cancelled_event,
    order_expired_event,
)

repo = OrderRepository()


async def create_order_from_event(  # Made async
    db: Session, 
    user_id: int, 
    reservation_id: int,
    showtime_id: int,
    seat_code: str,
):
    order = Order(
        user_id=user_id,
        reservation_id=reservation_id,
        pricing_snapshot={},
        final_amount=0,
        is_completed=False,
    )

    repo.create(db, order)

    event = order_created_event(
        order_id=order.id,
        reservation_id=reservation_id,
        user_id=user_id,
        showtime_id=showtime_id,
        seat_code=seat_code,
    )
    await publish_event_async(event["type"], event["payload"])  # Changed!

    return order


async def complete_order_from_event(  # Made async
    db: Session,  
    order_id: int  
):
    order = repo.get_order_by_id(db, order_id)
    if order is None:
        raise NotFoundError("Order not found")

    if order.is_completed:
        raise ConflictError("Order already completed")
    
    order.is_completed = True

    repo.save(db, order)

    event = order_completed_event(order.id)
    await publish_event_async(event["type"], event["payload"])  # Changed!

    return order


async def cancel_order_from_event(  # Made async
    db: Session,
    order_id: int
):
    order = repo.get_order_by_id(db, order_id)
    if order is None:
        raise NotFoundError("Order not found")

    event = order_cancelled_event(order.id)
    await publish_event_async(event["type"], event["payload"])  # Changed!

    return order


async def expire_order_from_event(  # Made async
    db: Session,
    order_id: int
):
    order = repo.get_order_by_id(db, order_id)
    if order is None:
        raise NotFoundError("Order not found")

    event = order_expired_event(order.id)
    await publish_event_async(event["type"], event["payload"])  # Changed!

    return order