# app/contexts/pricing/service.py

from sqlalchemy.orm import Session
from app.shared.services.event_publisher import publish_event_async  # <- Changed!

from .repository import PricingRepository
from .schemas import PriceCalculationResult
from .events import pricing_snapshot_created_event

repo = PricingRepository()

BASE_PRICE = 1000  


def calculate_price(db: Session) -> PriceCalculationResult:
    """
    Pure calculation function - remains sync since it's just math.
    This can be called from both sync and async contexts.
    """
    active_modifiers = repo.list_active_modifiers(db)

    price = BASE_PRICE
    applied = []

    for modifier in active_modifiers:
        # Add entry to snapshot
        applied.append({
            "name": modifier.name,
            "modifier_type": modifier.modifier_type,
            "amount": modifier.amount,
        })

        # Apply the math
        if modifier.modifier_type == "additive":
            price += modifier.amount
        elif modifier.modifier_type == "multiplicative":
            price *= modifier.amount

    return PriceCalculationResult(
        base_price=BASE_PRICE,
        modifiers_applied=applied,
        final_price=price,
    )


async def create_snapshot_from_event(
    db: Session,
    order_id: int,
) -> PriceCalculationResult:
    """
    Async service function for event handling.
    Calculates pricing and publishes event.
    """
    # Calculate pricing (sync operation)
    result = calculate_price(db)

    # Publish event using async version
    event = pricing_snapshot_created_event(
        order_id=order_id,
        snapshot=result.model_dump()
    )
    await publish_event_async(event["type"], event["payload"])  # <- Changed to async and await!

    return result