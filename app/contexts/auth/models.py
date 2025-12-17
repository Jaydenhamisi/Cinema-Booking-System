from sqlalchemy import Column, Integer, String, DateTime, func, Boolean

from app.core.database import Base


class UserCredential(Base):
    __tablename__ = "user_credentials"

    id = Column(Integer, primary_key=True, index=True)

    email = Column(String, unique=True, index=True, nullable=False)

    hashed_password = Column(String, nullable=False)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    is_active = Column(Boolean, nullable=False, default=True)