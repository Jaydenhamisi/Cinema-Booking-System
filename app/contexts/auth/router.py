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
async def register(  # Made async!
    payload: SignUpRequest,
    db: Session = Depends(get_db),
):
    auth_service = AuthService()
    
    # Register user
    user = await auth_service.register_user(db, payload)  # Added await!
    
    # Auto-login (return tokens)
    tokens = await auth_service.login(db, payload.email, payload.password)  # Added await!
    
    return tokens


# -----------------------------------------------------------
# Login
# -----------------------------------------------------------

@router.post(
    "/login",
    response_model=TokenResponse,
)
async def login(  # Made async!
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    auth_service = AuthService()
    token = await auth_service.login(  # Added await!
        db=db,
        email=form_data.username,
        password=form_data.password,
    )
    return token


# -----------------------------------------------------------
# Refresh (stays sync - no events)
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