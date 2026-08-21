from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.auth.dependencies import CurrentUser, require_role_permission
from app.services.synthesis_service import get_insight, list_insights

router = APIRouter()


class InsightResponse(BaseModel):
    insight_id: str
    query_id: str
    answer_text: str
    citations: list[dict]
    confidence: float | None
    status: str


class InsightListItem(BaseModel):
    insight_id: str
    query_id: str
    answer_preview: str
    confidence: float | None
    status: str
    created_at: str | None


@router.get("/api/insights", response_model=list[InsightListItem])
def list_insights_endpoint(
    status: str | None = None,
    limit: int = 50,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(require_role_permission("insights:read")),
):
    """List insights, optionally filtered by status (e.g. `pending_review`).
    Backs the Recommendation Workspace's browsable review queue."""
    insights = list_insights(db, status=status, limit=limit)
    return [
        InsightListItem(
            insight_id=i.id,
            query_id=i.query_id,
            answer_preview=(i.answer_text[:140] + "…") if len(i.answer_text) > 140 else i.answer_text,
            confidence=i.confidence,
            status=i.status,
            created_at=i.created_at.isoformat() if i.created_at else None,
        )
        for i in insights
    ]


@router.get("/api/insights/{insight_id}", response_model=InsightResponse)
def get_insight_endpoint(
    insight_id: str,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(require_role_permission("insights:read")),
):
    """Retrieve generated output, citations, and review status."""
    insight = get_insight(db, insight_id)
    if insight is None:
        raise HTTPException(status_code=404, detail="Insight not found")
    return InsightResponse(
        insight_id=insight.id,
        query_id=insight.query_id,
        answer_text=insight.answer_text,
        citations=insight.citations,
        confidence=insight.confidence,
        status=insight.status,
    )
