from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.errors import NotFoundError

from .repository import RefundRepository
from .models import Refund
from .schemas import RefundRead

repo = RefundRepository()

router = APIRouter(
    prefix="/refunds",
    tags=["refunds"],
)

@router.get("/{refund_id}", response_model=RefundRead)
def get_refund_by_id_route(
    refund_id: int,
    db: Session = Depends(get_db),
) -> Refund:
    
    refund = repo.get_refund_by_id(db, refund_id)
    if refund is None:
        raise NotFoundError("Refund not found")
    return refund


@router.get("/reservation/{reservation_id}", response_model=list[RefundRead])
def list_refunds_for_reservation_route(
    reservation_id: int,
    db: Session = Depends(get_db),
) -> list[Refund]:
    
    refund = repo.list_refunds_for_reservation(db, reservation_id)
    return refund