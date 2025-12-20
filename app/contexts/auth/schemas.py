from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Literal, Optional

class SignUpRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """
    Expected JWT payload structure after decoding.
    """
    sub: int                     # user id
    type: Literal["access", "refresh"]
    token_version: int
    exp: Optional[datetime] = None
    iat: Optional[datetime] = None


class UserCredentialResponse(BaseModel):
    id: int
    email: str
    is_active: bool
    created_at: datetime