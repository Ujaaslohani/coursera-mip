"""Processing-job state machine, per doc §4 Engineering Lead guidance:
'define every ingestion as a processing job... uploaded, preprocessed,
embedded, indexed, ... archived' (this project's scope covers uploaded
through indexed/failed — see app.database.models.JobStage).
"""
from sqlalchemy.orm import Session

from app.database.models import JobStage, ProcessingJob


def create_job(db: Session, asset_id: str) -> ProcessingJob:
    job = ProcessingJob(asset_id=asset_id, stage=JobStage.uploaded)
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def get_job(db: Session, job_id: str) -> ProcessingJob | None:
    return db.query(ProcessingJob).filter(ProcessingJob.id == job_id).first()


def advance_job(db: Session, job_id: str, stage: JobStage, error: str | None = None) -> ProcessingJob:
    job = get_job(db, job_id)
    if job is None:
        raise ValueError(f"processing job {job_id} not found")
    job.stage = stage
    job.error = error
    db.commit()
    db.refresh(job)
    return job
