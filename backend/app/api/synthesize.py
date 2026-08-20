from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.auth.dependencies import CurrentUser, require_role_permission
from app.services.synthesis_service import synthesize_insight
from app.services.audit_service import log_action

router = APIRouter()


class SynthesizeRequest(BaseModel):
    query_id: str
    retrieved_evidence: list[dict]


class SynthesizeResponse(BaseModel):
    insight_id: str
    answer_text: str
    citations: list[dict]
    confidence: float | None
    status: str


@router.post("/api/synthesize", response_model=SynthesizeResponse)
def synthesize_endpoint(
    payload: SynthesizeRequest,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(require_role_permission("query:run")),
):
    """Generate a grounded insight pack — citations, confidence, and a
    review-ready recommendation — from retrieved evidence only. The Quality
    Validator agent strips any citation that doesn't map to retrieved
    evidence before this ever reaches a reviewer."""
    insight = synthesize_insight(db, payload.query_id, payload.retrieved_evidence)
    log_action(db, actor=user.user_id, action="insight.synthesize", resource_type="insight", resource_id=insight.id,
               details={"query_id": payload.query_id, "confidence": insight.confidence})
    return SynthesizeResponse(
        insight_id=insight.id,
        answer_text=insight.answer_text,
        citations=insight.citations,
        confidence=insight.confidence,
        status=insight.status,
    )
