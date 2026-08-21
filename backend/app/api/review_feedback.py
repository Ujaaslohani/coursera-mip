from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.auth.dependencies import CurrentUser, require_role_permission
from app.services.review_service import submit_feedback
from app.services.audit_service import log_action

router = APIRouter()

_VALID_DECISIONS = {"accept", "edit", "reject", "escalate"}


class ReviewFeedbackRequest(BaseModel):
    insight_id: str
    decision: str  # accept | edit | reject | escalate
    notes: str | None = None


class ReviewFeedbackResponse(BaseModel):
    feedback_id: str
    insight_id: str
    decision: str


@router.post("/api/review-feedback", response_model=ReviewFeedbackResponse)
def submit_review_feedback(
    payload: ReviewFeedbackRequest,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(require_role_permission("review:write")),
):
    """Store accept, edit, reject, or escalate decisions on a generated
    insight. Human approval here is what makes a recommendation operational,
    per doc §5.4 'Human approval must be required before recommendations are
    treated as operationally approved actions.' Requires the `review:write`
    permission (reviewer/admin roles) — an educator-only token is correctly
    rejected with 403."""
    if payload.decision not in _VALID_DECISIONS:
        raise HTTPException(status_code=422, detail=f"decision must be one of {sorted(_VALID_DECISIONS)}")
    feedback = submit_feedback(
        db,
        insight_id=payload.insight_id,
        reviewer_id=user.user_id,
        decision=payload.decision,
        notes=payload.notes,
    )
    log_action(db, actor=user.user_id, action="insight.review", resource_type="insight",
               resource_id=payload.insight_id, details={"decision": payload.decision, "notes": payload.notes})
    return ReviewFeedbackResponse(feedback_id=feedback.id, insight_id=feedback.insight_id, decision=feedback.decision)
