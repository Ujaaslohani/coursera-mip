from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.auth.dependencies import CurrentUser, require_role_permission
from app.services.metrics_service import compute_metrics

router = APIRouter()


@router.get("/api/metrics")
def get_metrics(
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(require_role_permission("metrics:read")),
):
    """Pipeline health, review outcomes, and coverage counts for the
    Operations and Governance Dashboard (doc §5.3)."""
    return compute_metrics(db)
