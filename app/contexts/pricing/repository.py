# app/contexts/pricing/repository.py

from sqlalchemy.orm import Session
from sqlalchemy import select

from .models import PriceModifier


class PricingRepository:

    def get_modifier_by_id(self, db: Session, modifier_id: int):
        return db.get(PriceModifier, modifier_id)

    def list_modifiers(self, db: Session):
        stmt = select(PriceModifier)
        return db.scalars(stmt).all()

    def list_active_modifiers(self, db: Session):
        stmt = select(PriceModifier).where(PriceModifier.is_active == True)
        return db.scalars(stmt).all()

    def create_modifier(self, db: Session, modifier: PriceModifier):
        db.add(modifier)
        db.commit()
        db.refresh(modifier)
        return modifier

    def save_modifier(self, db: Session, modifier: PriceModifier):
        db.add(modifier)
        db.commit()
        db.refresh(modifier)
        return modifier

    def delete_modifier(self, db: Session, modifier: PriceModifier):
        db.delete(modifier)
        db.commit()
