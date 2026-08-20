from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database.models import Asset, Insight, JobStage, ProcessingJob, ReviewFeedback, Segment

# Backs GET /api/metrics, per doc §5.4 'Security, Logging, and Observability':
# operations dashboards must show pipeline health, failure rates, and
# retrieval-quality/review-outcome signals.


def compute_metrics(db: Session) -> dict:
    pipeline_health = {
        stage.value: db.query(ProcessingJob).filter(ProcessingJob.stage == stage).count()
        for stage in JobStage
    }
    review_outcomes = dict(
        db.query(ReviewFeedback.decision, func.count(ReviewFeedback.id))
        .group_by(ReviewFeedback.decision)
        .all()
    )
    return {
        "pipeline_health": pipeline_health,
        "review_outcomes": review_outcomes,
        "total_assets": db.query(Asset).count(),
        "total_segments_indexed": db.query(Segment).count(),
        "total_jobs": sum(pipeline_health.values()),
        "failed_jobs": pipeline_health.get(JobStage.failed.value, 0),
        "total_insights": db.query(Insight).count(),
        "pending_review": db.query(Insight).filter(Insight.status == "pending_review").count(),
    }
