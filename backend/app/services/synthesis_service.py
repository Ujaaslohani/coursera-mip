from sqlalchemy.orm import Session

from app.database.models import Insight, Query
from app.services.lifecycle_service import mark_segments_synthesized
from ai.synthesis.synthesizer import synthesize
from ai.retrieval.retriever import RetrievedEvidence
from ai.agents.quality_validator import validate


# Orchestration boundary for POST /api/synthesize, per doc §5.4 'LLM
# Synthesis and Recommendation Generation': the model must receive only
# retrieved evidence, and outputs must include citations, confidence notes,
# and recommended actions for review. The Quality Validator agent (doc
# §7.5) is the live gate that makes "no hallucinated claims" enforced, not
# just measured after the fact by ai/evaluation.


def synthesize_insight(db: Session, query_id: str, retrieved_evidence: list[dict]) -> Insight:
    if not retrieved_evidence:
        answer_text = "Insufficient evidence retrieved to synthesize a grounded insight."
        citations: list[dict] = []
        confidence = 0.0
    else:
        question = db.query(Query).filter(Query.id == query_id).first()
        evidence_objs = [RetrievedEvidence(**e) for e in retrieved_evidence]
        result = synthesize(question.question_text if question else "", evidence_objs)
        retrieved_ids = [e["segment_id"] for e in retrieved_evidence]
        result = validate(result, retrieved_ids)

        answer_text = result.get("answer", "")
        citations = result.get("citations", [])
        confidence = result.get("confidence")

        mark_segments_synthesized(db, [e["segment_id"] for e in retrieved_evidence])

    insight = Insight(
        query_id=query_id,
        answer_text=answer_text,
        citations=citations,
        confidence=confidence,
        status="pending_review",
    )
    db.add(insight)
    db.commit()
    db.refresh(insight)
    return insight


def get_insight(db: Session, insight_id: str) -> Insight | None:
    return db.query(Insight).filter(Insight.id == insight_id).first()


def list_insights(db: Session, status: str | None = None, limit: int = 50) -> list[Insight]:
    """Backs the Recommendation Workspace's pending-review list — without
    this, a reviewer needs to already know an insight_id to review anything."""
    query = db.query(Insight)
    if status:
        query = query.filter(Insight.status == status)
    return query.order_by(Insight.created_at.desc()).limit(limit).all()
