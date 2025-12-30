from sqlalchemy.orm import Session

from .models import AuditLogEntry
from .repository import AuditRepository


class AuditService:
    """Service for Audit business logic."""
    
    def __init__(self):
        self.repo = AuditRepository()
    
    async def write_audit_log(
        self,
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
        """Write an audit log entry."""
        entry = AuditLogEntry(
            actor_id=actor_id,
            actor_type=actor_type,
            action=action,
            target_type=target_type,
            target_id=target_id,
            payload=payload,
            request_id=request_id
        )

        return self.repo.create(db, entry)
    
    # ===== READ OPERATIONS (sync) =====
    
    def get_audit_log(self, db: Session, entry_id: int) -> AuditLogEntry | None:
        """Get audit log by ID."""
        return self.repo.get_by_id(db, entry_id)
    
    def list_audit_logs(
        self,
        db: Session,
        limit: int = 100,
        offset: int = 0
    ) -> list[AuditLogEntry]:
        """List audit logs with pagination."""
        return self.repo.list(db, limit=limit, offset=offset)