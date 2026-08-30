from fastapi import APIRouter, Depends

from app.models import (
    EmbeddingRefreshRequest,
    EmbeddingRefreshResponse,
    ProcessingJobCreateRequest,
    ProcessingJobResponse,
)
from app.services.operations_store import OperationsStore, get_operations_store
from app.services.qdrant_service import QdrantService, get_qdrant_service


router = APIRouter(prefix="/api", tags=["jobs"])


@router.post("/processing-jobs", response_model=ProcessingJobResponse)
def start_processing_job(
    request: ProcessingJobCreateRequest,
    store: OperationsStore = Depends(get_operations_store),
) -> ProcessingJobResponse:
    return store.start_processing_job(request.asset_id)


@router.get("/processing-jobs/{job_id}", response_model=ProcessingJobResponse)
def processing_job(
    job_id: str,
    store: OperationsStore = Depends(get_operations_store),
) -> ProcessingJobResponse:
    return store.get_job(job_id)


@router.post("/processing-jobs/{job_id}/archive", response_model=ProcessingJobResponse)
def archive_processing_job(
    job_id: str,
    store: OperationsStore = Depends(get_operations_store),
) -> ProcessingJobResponse:
    return store.archive_job(job_id)


@router.post("/embeddings", response_model=EmbeddingRefreshResponse)
def refresh_embeddings(
    request: EmbeddingRefreshRequest,
    service: QdrantService = Depends(get_qdrant_service),
) -> EmbeddingRefreshResponse:
    point_ids = request.segment_ids + request.qdrant_record_ids
    return service.verify_embeddings(point_ids)
