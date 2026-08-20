from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.auth.dependencies import CurrentUser, require_role_permission
from app.database.models import JobStage
from app.jobs.job_queue import create_job, get_job, advance_job
from app.services.processing_service import run_processing_job
from app.services.audit_service import log_action

router = APIRouter()


class ProcessingJobCreateRequest(BaseModel):
    asset_id: str


class ProcessingJobResponse(BaseModel):
    job_id: str
    asset_id: str
    stage: str
    error: str | None = None


@router.post("/api/processing-jobs", response_model=ProcessingJobResponse)
def start_processing_job(
    payload: ProcessingJobCreateRequest,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(require_role_permission("processing:write")),
):
    """Start preprocessing, segmentation, extraction, and metadata normalization.
    Runs synchronously (no queue/worker infra in this project's scope) and
    advances the job through preprocessed -> embedded -> indexed -> searchable,
    or fails visibly to `failed` with a reason (see processing_service.ProcessingError)."""
    job = create_job(db, payload.asset_id)
    job = run_processing_job(db, job.id)
    log_action(db, actor=user.user_id, action="processing_job.run", resource_type="processing_job",
               resource_id=job.id, details={"asset_id": job.asset_id, "final_stage": job.stage.value, "error": job.error})
    return ProcessingJobResponse(job_id=job.id, asset_id=job.asset_id, stage=job.stage.value, error=job.error)


@router.get("/api/processing-jobs/{job_id}", response_model=ProcessingJobResponse)
def get_processing_job(
    job_id: str,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(require_role_permission("processing:write")),
):
    """Retrieve job status, warnings, failures, and output records."""
    job = get_job(db, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Processing job not found")
    return ProcessingJobResponse(job_id=job.id, asset_id=job.asset_id, stage=job.stage.value, error=job.error)


@router.post("/api/processing-jobs/{job_id}/archive", response_model=ProcessingJobResponse)
def archive_processing_job(
    job_id: str,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(require_role_permission("processing:write")),
):
    """Explicitly retire an asset from active operations — the final step of
    the 9-stage lifecycle (doc §4): 'uploaded, ..., reviewed, and archived.'
    Unlike the other 8 stages, archiving is never automatic."""
    job = get_job(db, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Processing job not found")
    job = advance_job(db, job_id, JobStage.archived)
    log_action(db, actor=user.user_id, action="processing_job.archive", resource_type="processing_job",
               resource_id=job.id, details={"asset_id": job.asset_id})
    return ProcessingJobResponse(job_id=job.id, asset_id=job.asset_id, stage=job.stage.value, error=job.error)
