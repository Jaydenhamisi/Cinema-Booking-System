from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from .service import AuthService
from .repository import UserCredentialRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

auth_service = AuthService()
user_repo = UserCredentialRepository()


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    """
    Extracts the authenticated user from the JWT token.
    """
    user_id = auth_service.verify_token(token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
        )

    user = user_repo.get(db, user_id)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User inactive or not found",
        )

    return user


def get_current_admin(
    current_user = Depends(get_current_user)
):
    """
    Only admins can access admin endpoints.
    """
    if current_user.user_type != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )
    return current_user
