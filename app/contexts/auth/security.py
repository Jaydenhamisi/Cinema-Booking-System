# app/core/security.py
from datetime import datetime, timedelta, timezone
from typing import Any, Dict

from jose import jwt, JWTError
from passlib.context import CryptContext

from app.core.config import settings


pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)


# Password Hashing

def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# JWT Creation Helper

def _build_token_payload(
    *,
    user_id: int,
    token_type: str,
    token_version: int,
    expires_delta: timedelta,
) -> Dict[str, Any]:
    now = datetime.now(timezone.utc)
    expire = now + expires_delta

    return {
        "sub": str(user_id),
        "type": token_type,
        "token_version": token_version,
        "iat": now,
        "exp": expire,
    }


def create_access_token(*, user_id: int, token_version: int = 0) -> str:
    """
    Creates a short-lived access token.
    
    Args:
        user_id: The user's ID to encode in the token
        token_version: Token version for invalidation (default 0)
    
    Returns:
        Encoded JWT access token string
    """
    payload = _build_token_payload(
        user_id=user_id,
        token_type="access",
        token_version=token_version,
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(*, user_id: int, token_version: int = 0) -> str:
    """
    Creates a long-lived refresh token.
    
    Args:
        user_id: The user's ID to encode in the token
        token_version: Token version for invalidation (default 0)
    
    Returns:
        Encoded JWT refresh token string
    """
    payload = _build_token_payload(
        user_id=user_id,
        token_type="refresh",
        token_version=token_version,
        expires_delta=timedelta(days=7),  # 7 days for refresh
    )
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


# JWT Decoding

def decode_token(token: str) -> dict:
    """
    Decodes and validates a JWT token.
    
    Args:
        token: The JWT token string to decode
    
    Returns:
        The decoded payload as a dictionary
    
    Raises:
        JWTError: If token is invalid, expired, or malformed
    """
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])