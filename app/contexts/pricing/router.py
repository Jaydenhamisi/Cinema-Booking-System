# app/contexts/pricing/router.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.errors import NotFoundError

from .repository import PricingRepository
from .models import PriceModifier
from .schemas import (
    PriceModifierCreate,
    PriceModifierUpdate,
    PriceModifierRead,
)

router = APIRouter()
repo = PricingRepository()


@router.post("/modifiers", response_model=PriceModifierRead)
def create_modifier(
    data: PriceModifierCreate,
    db: Session = Depends(get_db),
):
    modifier = PriceModifier(
        name=data.name,
        modifier_type=data.modifier_type,
        amount=data.amount,
        applies_to=data.applies_to,
        is_active=data.is_active,
    )

    repo.create_modifier(db, modifier)
    return modifier


@router.get("/modifiers", response_model=list[PriceModifierRead])
def list_modifiers(
    db: Session = Depends(get_db),
):
    return repo.list_modifiers(db)


@router.get("/modifiers/{modifier_id}", response_model=PriceModifierRead)
def get_modifier(
    modifier_id: int,
    db: Session = Depends(get_db),
):
    modifier = repo.get_modifier_by_id(db, modifier_id)
    if not modifier:
        raise HTTPException(404, "Modifier not found")
    return modifier


@router.patch("/modifiers/{modifier_id}", response_model=PriceModifierRead)
def update_modifier(
    modifier_id: int,
    data: PriceModifierUpdate,
    db: Session = Depends(get_db),
):
    modifier = repo.get_modifier_by_id(db, modifier_id)
    if not modifier:
        raise HTTPException(404, "Modifier not found")

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

    repo.save_modifier(db, modifier)
    return modifier


@router.delete("/modifiers/{modifier_id}")
def delete_modifier(
    modifier_id: int,
    db: Session = Depends(get_db),
):
    modifier = repo.get_modifier_by_id(db, modifier_id)
    if not modifier:
        raise HTTPException(404, "Modifier not found")

    repo.delete_modifier(db, modifier)
    return {"status": "deleted"}
