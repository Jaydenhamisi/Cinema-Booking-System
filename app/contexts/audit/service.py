from sqlalchemy.orm import Session

from .models import AuditLogEntry
from .repository import AuditRepository

repo = AuditRepository()


def write_audit_log(
        db: Session,
        *,
        actor_id: int | None,
        actor_type: str,
        action: str,
        target_type: str,
        target_id: int,
        payload: dict,
        request_id: int | None = None,
) -> AuditLogEntry:
    
    entry = AuditLogEntry(
        actor_id=actor_id,
        actor_type=actor_type,
        action=action,
        target_type=target_type,
        target_id=target_id,
        payload=payload,
        request_id=request_id
    )

    return repo.create(db, entry)