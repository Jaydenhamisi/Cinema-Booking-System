# app/contexts/pricing/service.py

from sqlalchemy.orm import Session
from app.shared.services.event_publisher import publish_event

from .repository import PricingRepository
from .schemas import PriceCalculationResult
from .events import pricing_snapshot_created_event  # we will define later

repo = PricingRepository()


BASE_PRICE = 1000  # Phase B simple constant

def calculate_price(db: Session) -> PriceCalculationResult:
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


def create_snapshot_from_event(
    db: Session,
    order_id: int,
):
    result = calculate_price(db)

    # Publish event for OrderContext to receive
    event = pricing_snapshot_created_event(
        order_id=order_id,
        snapshot=result.model_dump()
    )
    publish_event(event["type"], event["payload"])

    return result

