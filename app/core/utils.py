# app/core/utils.py
from datetime import datetime, timezone
import uuid


def generate_uuid_str() -> str:
    return str(uuid.uuid4())


def utcnow() -> datetime:
    """Always return a timezone-aware UTC datetime."""
    return datetime.now(timezone.utc)


