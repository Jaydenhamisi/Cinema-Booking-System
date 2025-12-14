from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    JSON
)

from app.core.database import Base

class AuditLogEntry(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)

    actor_id = Column(Integer, nullable=False)

    actor_type = Column(String, nullable=False)

    action = Column(String, nullable=False)

    target_id = Column(Integer, nullable=False)

    target_type = Column(String, nullable=False)

    payload = Column(JSON, nullable=False)

    request_id = Column(Integer, nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )