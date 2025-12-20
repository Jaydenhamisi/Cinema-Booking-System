from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.contexts.auth.schemas import (
    SignUpRequest,
    TokenResponse,
    RefreshTokenRequest,
)
from app.contexts.auth.service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


# -----------------------------------------------------------
# Register
# -----------------------------------------------------------

@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    payload: SignUpRequest,
    db: Session = Depends(get_db),
):
    auth_service = AuthService()
    
    # Register user
    user = auth_service.register_user(db, payload)
    
    # Auto-login (return tokens)
    tokens = auth_service.login(db, payload.email, payload.password)
    
    return tokens


# -----------------------------------------------------------
# Login
# -----------------------------------------------------------

@router.post(
    "/login",
    response_model=TokenResponse,
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    auth_service = AuthService()
    token = auth_service.login(
        db=db,
        email=form_data.username,
        password=form_data.password,
    )
    return token


# -----------------------------------------------------------
# Refresh
# -----------------------------------------------------------

@router.post(
    "/refresh",
    response_model=TokenResponse,
)
def refresh(
    payload: RefreshTokenRequest,
    db: Session = Depends(get_db),
):
    auth_service = AuthService()
    token = auth_service.refresh_tokens(db, payload.refresh_token)
    return token