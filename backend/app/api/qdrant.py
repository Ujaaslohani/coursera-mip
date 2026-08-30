from fastapi import APIRouter, Depends, Query

from app.models import (
    CollectionResponse,
    MetadataOptionsResponse,
    MetricsResponse,
    RecordResponse,
    ScrollResponse,
)
from app.services.qdrant_service import QdrantService, get_qdrant_service


router = APIRouter(prefix="/api", tags=["qdrant"])


@router.get("/qdrant/collection", response_model=CollectionResponse)
def collection(
    service: QdrantService = Depends(get_qdrant_service),
) -> CollectionResponse:
    return service.get_collection()


@router.get("/qdrant/records", response_model=ScrollResponse)
def records(
    limit: int = Query(default=10, ge=1, le=100),
    offset: str | None = None,
    service: QdrantService = Depends(get_qdrant_service),
) -> ScrollResponse:
    return service.scroll_records(limit=limit, offset=offset)


@router.get("/qdrant/records/{point_id}", response_model=RecordResponse)
def record(
    point_id: str,
    service: QdrantService = Depends(get_qdrant_service),
) -> RecordResponse:
    return service.get_record(point_id)


@router.get("/evidence/{point_id}", response_model=RecordResponse)
def evidence(
    point_id: str,
    service: QdrantService = Depends(get_qdrant_service),
) -> RecordResponse:
    return service.get_record(point_id)


@router.get("/segments/{segment_id}", response_model=RecordResponse)
def segment(
    segment_id: str,
    service: QdrantService = Depends(get_qdrant_service),
) -> RecordResponse:
    return service.get_record(segment_id)


@router.get("/metadata/options", response_model=MetadataOptionsResponse)
def metadata_options(
    scan_limit: int = Query(default=5000, ge=1, le=10000),
    service: QdrantService = Depends(get_qdrant_service),
) -> MetadataOptionsResponse:
    return service.metadata_options(scan_limit=scan_limit)


@router.get("/metrics", response_model=MetricsResponse)
def metrics(
    scan_limit: int = Query(default=5000, ge=1, le=10000),
    service: QdrantService = Depends(get_qdrant_service),
) -> MetricsResponse:
    return service.metrics(scan_limit=scan_limit)
