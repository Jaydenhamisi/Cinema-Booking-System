from app.core.database import SessionLocal
from app.core.event_bus import event_bus

from app.contexts.refund.service import issue_refund_from_event
from app.contexts.order.repository import OrderRepository
from app.contexts.payment.repository import PaymentRepository
from app.contexts.reservation.repository import ReservationRepository

order_repo = OrderRepository()
payment_repo = PaymentRepository()
reservation_repo = ReservationRepository()

async def on_reservation_cancelled(payload: dict):
    reservation_id = payload.get("reservation_id")
    if not reservation_id:
        return

    db = SessionLocal()
    try:
        order = order_repo.get_order_by_reservation_id(db, reservation_id)
        if not order:
            return

        payment_attempts = payment_repo.list_payment_attempts_for_order(
            db,
            order_id=order.id
        )
        if not payment_attempts:
            return

        payment_attempt = payment_attempts[0]  

        issue_refund_from_event(
            db,
            reservation_id=reservation_id,
            payment_attempt_id=payment_attempt.id,
            reason="reservation_cancelled"
        )
    finally:
        db.close()


        
        