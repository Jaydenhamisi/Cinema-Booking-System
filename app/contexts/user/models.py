from enum import Enum as PyEnum
from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    String,
    DateTime,
    func,
    Enum as SAEnum
)

from app.core.database import Base

class UserTypeEnum(str, PyEnum):
    USER = "user"
    ADMIN = "admin"

class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)
    
    # One profile per auth user
    user_id = Column(
        Integer, 
        ForeignKey("user_credentials.id"), 
        unique=True, 
        nullable=False,
        index=True
    )
    
    # Profile data
    name = Column(String, nullable=True)  
    email = Column(String, nullable=False, index=True)  # Copy from Auth, NOT unique
    user_type = Column(SAEnum(UserTypeEnum), default=UserTypeEnum.USER, index=True)
    
    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now())