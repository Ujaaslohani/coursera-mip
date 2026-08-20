"""Advances a processing job through the `retrieved` / `synthesized` /
`reviewed` stages as ITS OWN segments actually participate in a live query,
a synthesized insight, and a reviewed insight — not merely once indexing
finishes. `searchable` advances immediately after `indexed` (see
processing_service.run_processing_job); `archived` is a manual action.

Lifecycle marking is keyed off Segment.job_id — the specific job that
created each segment — rather than "the asset's most recent job." An asset
can accumulate multiple job rows over time (each re-processing run creates
a new one); picking "latest" would silently advance the WRONG job's stage
whenever a newer, unrelated job exists for the same asset. This is what
makes the full 9-stage lifecycle from doc §4 real: a job's stage reflects
how far the evidence IT PRODUCED has actually traveled through the
pipeline, not a status flag on an arbitrary row.
"""
from sqlalchemy.orm import Session

from app.database.models import JobStage, JOB_STAGE_PROGRESSION, ProcessingJob, Segment
from app.jobs.job_queue import advance_job, get_job


def advance_if_later(db: Session, job: ProcessingJob, new_stage: JobStage) -> None:
    if job.stage == JobStage.failed:
        return  # failed is terminal — a later query/synthesis/review shouldn't paper over it
    try:
        if JOB_STAGE_PROGRESSION.index(new_stage) <= JOB_STAGE_PROGRESSION.index(job.stage):
            return
    except ValueError:
        return
    advance_job(db, job.id, new_stage)


def _jobs_for_segments(db: Session, segment_ids: list[str]) -> list[ProcessingJob]:
    if not segment_ids:
        return []
    job_ids = {
        row[0]
        for row in db.query(Segment.job_id).filter(Segment.id.in_(segment_ids), Segment.job_id.is_not(None)).all()
    }
    return [job for job in (get_job(db, jid) for jid in job_ids) if job is not None]


def mark_segments_retrieved(db: Session, segment_ids: list[str]) -> None:
    for job in _jobs_for_segments(db, segment_ids):
        advance_if_later(db, job, JobStage.retrieved)


def mark_segments_synthesized(db: Session, segment_ids: list[str]) -> None:
    for job in _jobs_for_segments(db, segment_ids):
        advance_if_later(db, job, JobStage.synthesized)


def mark_segments_reviewed(db: Session, segment_ids: list[str]) -> None:
    for job in _jobs_for_segments(db, segment_ids):
        advance_if_later(db, job, JobStage.reviewed)
