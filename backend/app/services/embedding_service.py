from sqlalchemy.orm import Session

from app.database.models import Segment, JobStage
from app.jobs.job_queue import advance_job
from ai.embeddings.embed import embed_segment

# NOTE: modality-specific preprocessing (frame extraction, OCR, transcript
# alignment) lives in the pipelines/ repo and populates Segment.text_content
# upstream of this step. This service is the backend-side orchestration
# boundary described in doc §7.3 (POST /api/embeddings).


def refresh_embeddings(db: Session, segment_ids: list[str]) -> int:
    segments = db.query(Segment).filter(Segment.id.in_(segment_ids)).all()
    updated = 0
    for segment in segments:
        if not segment.text_content:
            continue  # nothing to embed until preprocessing has populated text
        segment.embedding = embed_segment(segment.text_content)
        updated += 1
    db.commit()
    return updated


def mark_asset_embedded(db: Session, job_id: str):
    advance_job(db, job_id, JobStage.embedded)
