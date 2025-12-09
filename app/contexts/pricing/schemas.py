# app/contexts/pricing/schemas.py

from typing import Optional, Dict, Literal, List
from pydantic import BaseModel


class PriceModifierBase(BaseModel):
    name: str
    modifier_type: Literal["additive", "multiplicative"]
    amount: float
    applies_to: Optional[Dict] = None
    is_active: bool = True


class PriceModifierCreate(PriceModifierBase):
    pass


class PriceModifierUpdate(BaseModel):
    name: Optional[str] = None
    modifier_type: Optional[Literal["additive", "multiplicative"]] = None
    amount: Optional[float] = None
    applies_to: Optional[Dict] = None
    is_active: Optional[bool] = None


class PriceModifierRead(PriceModifierBase):
    id: int

    model_config = {"from_attributes": True}


class PriceCalculationResult(BaseModel):
    base_price: float
    final_price: float
    modifiers_applied: List[Dict]
