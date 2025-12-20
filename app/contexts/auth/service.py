from typing import Tuple

from fastapi import HTTPException, status
from jose import JWTError
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.contexts.auth.schemas import SignUpRequest, TokenResponse, TokenPayload
from .security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.contexts.auth.repository import AuthRepository
from app.shared.services.event_publisher import publish_event


class AuthService:
    """
    Orchestrates auth flows:
    - registration
    - login
    - token refresh
    """

    def __init__(self):
        self.repo = AuthRepository()

    # -------------------------------------------------------
    # Registration
    # -------------------------------------------------------

    def register_user(self, db: Session, payload: SignUpRequest):
        existing = self.repo.get_user_by_email(db, payload.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        hashed = hash_password(payload.password)
        user = self.repo.create_user(db, email=payload.email, hashed_password=hashed)
        
        # Emit event
        publish_event("auth.user_registered", {
            "user_id": user.id,
            "email": user.email,
        })
        
        return user

    # -------------------------------------------------------
    # Login
    # -------------------------------------------------------

    def authenticate_user(self, db: Session, email: str, password: str):
        user = self.repo.get_user_by_email(db, email)
        if not user:
            return None

        if not verify_password(password, user.hashed_password):
            return None

        return user

    def login(self, db: Session, email: str, password: str) -> TokenResponse:
        user = self.authenticate_user(db, email, password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        access_token, refresh_token = self._issue_token_pair(
            user_id=user.id,
            token_version=user.token_version,
        )
        
        # Emit event
        publish_event("auth.user_logged_in", {
            "user_id": user.id,
            "email": user.email,
        })

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
        )

    # -------------------------------------------------------
    # Refresh
    # -------------------------------------------------------

    def refresh_tokens(self, db: Session, refresh_token: str) -> TokenResponse:
        try:
            payload_dict = decode_token(refresh_token)
            payload = TokenPayload(**payload_dict)
        except (JWTError, ValidationError):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if payload.type != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type for refresh",
            )

        user = self.repo.get_user_by_id(db, payload.sub)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
            )

        # Check token_version invariant
        if payload.token_version != user.token_version:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been revoked",
            )

        access_token, new_refresh_token = self._issue_token_pair(
            user_id=user.id,
            token_version=user.token_version,
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=new_refresh_token,
        )

    # -------------------------------------------------------
    # Internal helpers
    # -------------------------------------------------------

    def _issue_token_pair(self, *, user_id: int, token_version: int) -> Tuple[str, str]:
        access_token = create_access_token(
            user_id=user_id,
            token_version=token_version,
        )
        refresh_token = create_refresh_token(
            user_id=user_id,
            token_version=token_version,
        )
        return access_token, refresh_token
