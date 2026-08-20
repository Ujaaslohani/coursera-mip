from sqlalchemy.orm import Session

from app.database.models import Insight, ReviewFeedback
from app.services.lifecycle_service import mark_segments_reviewed

# Orchestration boundary for POST /api/review-feedback, per doc §5.4 'Human
# Review, Governance, and Feedback': reviewer decisions must be stored, and
# human approval is required before a recommendation counts as an approved
# action — the insight's own status field records that decision. The assets
# behind the insight's citations are advanced to JobStage.reviewed here,
# completing the full 9-stage lifecycle for evidence that made it all the
# way to a human decision.


def submit_feedback(db: Session, insight_id: str, reviewer_id: str, decision: str, notes: str | None) -> ReviewFeedback:
    feedback = ReviewFeedback(insight_id=insight_id, reviewer_id=reviewer_id, decision=decision, notes=notes)
    db.add(feedback)

    insight = db.query(Insight).filter(Insight.id == insight_id).first()
    if insight is not None:
        insight.status = decision
        cited_segment_ids = [c["segment_id"] for c in (insight.citations or []) if "segment_id" in c]
        mark_segments_reviewed(db, cited_segment_ids)

    db.commit()
    db.refresh(feedback)
    return feedback
