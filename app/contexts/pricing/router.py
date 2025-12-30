# app/contexts/pricing/router.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.errors import NotFoundError
from app.contexts.auth.dependencies import get_current_user

from .service import PricingService
from .models import PriceModifier
from .schemas import (
    PriceModifierCreate,
    PriceModifierUpdate,
    PriceModifierRead,
)

router = APIRouter(
    prefix="/pricing",
    tags=["pricing"],
)

# Create service instance
pricing_service = PricingService()


@router.post("/modifiers", response_model=PriceModifierRead)
async def create_modifier(
    data: PriceModifierCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    modifier = PriceModifier(
        name=data.name,
        modifier_type=data.modifier_type,
        amount=data.amount,
        applies_to=data.applies_to,
        is_active=data.is_active,
    )

    return await pricing_service.create_modifier(db, modifier, user_id=current_user.id)


@router.get("/modifiers", response_model=list[PriceModifierRead])
def list_modifiers(
    db: Session = Depends(get_db),
):
    return pricing_service.list_modifiers(db)


@router.get("/modifiers/{modifier_id}", response_model=PriceModifierRead)
def get_modifier(
    modifier_id: int,
    db: Session = Depends(get_db),
):
    modifier = pricing_service.get_modifier(db, modifier_id)
    if not modifier:
        raise NotFoundError("Modifier not found")
    return modifier


@router.patch("/modifiers/{modifier_id}", response_model=PriceModifierRead)
async def update_modifier(
    modifier_id: int,
    data: PriceModifierUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    modifier = pricing_service.get_modifier(db, modifier_id)
    if not modifier:
        raise NotFoundError("Modifier not found")

    # Update only fields provided
    if data.name is not None:
        modifier.name = data.name
    if data.modifier_type is not None:
        modifier.modifier_type = data.modifier_type
    if data.amount is not None:
        modifier.amount = data.amount
    if data.applies_to is not None:
        modifier.applies_to = data.applies_to
    if data.is_active is not None:
        modifier.is_active = data.is_active

    return await pricing_service.update_modifier(db, modifier, user_id=current_user.id)


@router.delete("/modifiers/{modifier_id}")
async def delete_modifier(
    modifier_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    modifier = pricing_service.get_modifier(db, modifier_id)
    if not modifier:
        raise NotFoundError("Modifier not found")

    pricing_service.repo.delete_modifier(db, modifier)
    
    await pricing_service.delete_modifier(db, modifier_id, user_id=current_user.id)
    
    return {"status": "deleted"}