from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.contexts.auth.dependencies import get_current_user
from .schemas import UserProfileResponse, UserProfileUpdate
from .service import UserProfileService

service = UserProfileService()

router = APIRouter(
    prefix="/profiles",
    tags=["profiles"],
)


@router.get("/me", response_model=UserProfileResponse)
def get_my_profile(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """Get authenticated user's profile"""
    return service.get_profile(db, current_user.id)


@router.patch("/me", response_model=UserProfileResponse)
def update_my_profile(
    payload: UserProfileUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """Update authenticated user's profile"""
    return service.update_profile(db, current_user.id, payload)