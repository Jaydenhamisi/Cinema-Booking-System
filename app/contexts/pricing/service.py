# app/contexts/pricing/service.py
from sqlalchemy.orm import Session
from app.shared.services.event_publisher import publish_event_async

from .repository import PricingRepository
from .schemas import PriceCalculationResult
from .events import (
    pricing_snapshot_created_event,
    pricing_modifier_created_event,
    pricing_modifier_updated_event,
    pricing_modifier_deleted_event,
)
from .models import PriceModifier

BASE_PRICE = 1000


class PricingService:
    """Service for Pricing business logic."""
    
    def __init__(self):
        self.repo = PricingRepository()

    def calculate_price(self, db: Session) -> PriceCalculationResult:
        """
        Pure calculation function - stays sync since it's just math.
        This can be called from both sync and async contexts.
        """
        active_modifiers = self.repo.list_active_modifiers(db)

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
        self,
        db: Session,
        order_id: int,
    ) -> PriceCalculationResult:
        """
        Async service function for event handling.
        Calculates pricing and publishes event.
        """
        # Calculate pricing (sync operation)
        result = self.calculate_price(db)

        # Publish event using async version
        event = pricing_snapshot_created_event(
            order_id=order_id,
            snapshot=result.model_dump()
        )
        await publish_event_async(event["type"], event["payload"])

        return result
    
    # ===== MODIFIER CRUD (for admin) =====
    
    async def create_modifier(
        self,
        db: Session,
        modifier: PriceModifier,
        user_id: int = None,
    ):
        """Create a new pricing modifier."""
        modifier = self.repo.create_modifier(db, modifier)
        
        event = pricing_modifier_created_event(modifier.id, user_id=user_id)
        await publish_event_async(event["type"], event["payload"])
        
        return modifier
    
    async def update_modifier(
        self,
        db: Session,
        modifier: PriceModifier,
        user_id: int = None,
    ):
        """Update a pricing modifier."""
        modifier = self.repo.save_modifier(db, modifier)
        
        event = pricing_modifier_updated_event(modifier.id, user_id=user_id)
        await publish_event_async(event["type"], event["payload"])
        
        return modifier
    
    async def delete_modifier(
        self,
        db: Session,
        modifier_id: int,
        user_id: int = None,
    ):
        """Delete a pricing modifier."""
        event = pricing_modifier_deleted_event(modifier_id, user_id=user_id)
        await publish_event_async(event["type"], event["payload"])
    
    # ===== READ OPERATIONS (sync) =====
    
    def get_modifier(self, db: Session, modifier_id: int):
        """Get modifier by ID."""
        return self.repo.get_modifier_by_id(db, modifier_id)
    
    def list_modifiers(self, db: Session):
        """List all modifiers."""
        return self.repo.list_modifiers(db)