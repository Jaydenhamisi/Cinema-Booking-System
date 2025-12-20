from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError

from app.core.database import get_db
from app.contexts.auth.security import decode_token
from .service import AuthService
from .repository import AuthRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

user_repo = AuthRepository()


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    """
    Extracts the authenticated user from the JWT token.
    """
    try:
        payload = decode_token(token)
        user_id = int(payload.get("sub"))
        
        # Verify it's an access token
        if payload.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
            )
    except (JWTError, ValueError, KeyError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = user_repo.get_user_by_id(db, user_id)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User inactive or not found",
        )
    
    return user


def get_current_admin(
    current_user = Depends(get_current_user),
):
    """
    Only admins can access admin endpoints.
    Assumes user_type field exists on UserCredential.
    """
    if current_user.user_type != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )
    return current_user


def get_auth_service() -> AuthService:
    """Returns an AuthService instance"""
    return AuthService()