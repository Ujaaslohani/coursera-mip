from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.auth.dependencies import CurrentUser, require_role_permission
from app.services.audit_service import list_recent

router = APIRouter()


class AuditLogEntry(BaseModel):
    id: str
    actor: str
    action: str
    resource_type: str | None
    resource_id: str | None
    details: dict
    created_at: str


@router.get("/api/audit-log", response_model=list[AuditLogEntry])
def get_audit_log(
    limit: int = 50,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(require_role_permission("audit:read")),
):
    """Audit-ready record of every mutating action, per doc §5.4 governance:
    'audit-ready records.' Requires the `audit:read` permission
    (analyst/admin roles)."""
    entries = list_recent(db, limit=limit)
    return [
        AuditLogEntry(
            id=e.id, actor=e.actor, action=e.action, resource_type=e.resource_type,
            resource_id=e.resource_id, details=e.details or {}, created_at=e.created_at.isoformat(),
        )
        for e in entries
    ]
