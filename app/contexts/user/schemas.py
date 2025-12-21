from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime

from .models import UserTypeEnum


class UserProfileCreate(BaseModel):
    """
    Created by event handler when user registers.
    """
    user_id: int
    email: EmailStr
    name: Optional[str] = None


class UserProfileUpdate(BaseModel):
    """What regular users can update"""
    name: Optional[str] = None
    email: Optional[EmailStr] = None


class UserProfileResponse(BaseModel):
    """Profile data returned by API"""
    id: int
    user_id: int
    name: Optional[str]
    email: EmailStr
    user_type: UserTypeEnum
    created_at: datetime
    
    model_config = {"from_attributes": True}


class AdminUpdateUserType(BaseModel):
    """Admin-only: change user type"""
    user_type: UserTypeEnum