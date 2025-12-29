from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from ..auth.dependencies import get_current_user

from .schemas import OrderRead
from .repository import OrderRepository

repo = OrderRepository()

router = APIRouter(
    prefix="/orders",
    tags=["orders"],
)


@router.get("/", response_model=list[OrderRead])
def list_user_orders(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    return repo.list_orders(
        db=db,
        user_id=current_user.id,
        completed_only=False
    )

    

