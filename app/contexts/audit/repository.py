# app/contexts/audit/repository.py

from sqlalchemy.orm import Session
from sqlalchemy import select

from .models import AuditLogEntry


class AuditRepository:

    def create(
        self,
        db: Session,
        entry: AuditLogEntry
    ) -> AuditLogEntry:
        db.add(entry)
        db.commit()
        db.refresh(entry)
        return entry

    def get_by_id(
        self,
        db: Session,
        entry_id: int
    ) -> AuditLogEntry | None:
        return db.get(AuditLogEntry, entry_id)

    def list(
        self,
        db: Session,
        limit: int = 100,
        offset: int = 0
    ) -> list[AuditLogEntry]:
        stmt = (
            select(AuditLogEntry)
            .order_by(AuditLogEntry.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return db.scalars(stmt).all()
