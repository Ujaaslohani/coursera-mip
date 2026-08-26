from fastapi import Depends, FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

from app.config import Settings, get_settings
from app.models import (
    AssetListResponse,
    CollectionResponse,
    ContextRequest,
    ContextResponse,
    HealthResponse,
    MetadataOptionsResponse,
    MetricsResponse,
    QueryRequest,
    QueryResponse,
    RecordResponse,
    ScrollResponse,
)
from app.services.qdrant_service import QdrantService, get_qdrant_service


settings = get_settings()

app = FastAPI(
    title="Coursera Multimodal Intelligence Backend",
    description="Backend API for Qdrant-backed multimodal evidence retrieval.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.frontend_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
def health(config: Settings = Depends(get_settings)) -> HealthResponse:
    return HealthResponse(
        status="ok",
        qdrant_url_configured=bool(config.qdrant_url),
        qdrant_collection=config.qdrant_collection,
        embedding_model=config.embedding_model,
    )


@app.get("/api/qdrant/collection", response_model=CollectionResponse)
def collection(
    service: QdrantService = Depends(get_qdrant_service),
) -> CollectionResponse:
    return service.get_collection()


@app.get("/api/qdrant/records", response_model=ScrollResponse)
def records(
    limit: int = Query(default=10, ge=1, le=100),
    offset: str | None = None,
    service: QdrantService = Depends(get_qdrant_service),
) -> ScrollResponse:
    return service.scroll_records(limit=limit, offset=offset)


@app.get("/api/qdrant/records/{point_id}", response_model=RecordResponse)
def record(
    point_id: str,
    service: QdrantService = Depends(get_qdrant_service),
) -> RecordResponse:
    return service.get_record(point_id)


@app.get("/api/evidence/{point_id}", response_model=RecordResponse)
def evidence(
    point_id: str,
    service: QdrantService = Depends(get_qdrant_service),
) -> RecordResponse:
    return service.get_record(point_id)


@app.post("/api/query", response_model=QueryResponse)
def query(
    request: QueryRequest,
    config: Settings = Depends(get_settings),
    service: QdrantService = Depends(get_qdrant_service),
) -> QueryResponse:
    results = service.semantic_search(
        query=request.query,
        top_k=request.top_k,
        filters=request.filters,
    )
    return QueryResponse(
        query=request.query,
        top_k=request.top_k,
        collection_name=config.qdrant_collection,
        results=results,
    )


@app.post("/api/context", response_model=ContextResponse)
def context(
    request: ContextRequest,
    service: QdrantService = Depends(get_qdrant_service),
) -> ContextResponse:
    return service.build_context(
        query=request.query,
        top_k=request.top_k,
        filters=request.filters,
    )


@app.get("/api/metadata/options", response_model=MetadataOptionsResponse)
def metadata_options(
    scan_limit: int = Query(default=5000, ge=1, le=10000),
    service: QdrantService = Depends(get_qdrant_service),
) -> MetadataOptionsResponse:
    return service.metadata_options(scan_limit=scan_limit)


@app.get("/api/assets", response_model=AssetListResponse)
def assets(
    limit: int = Query(default=50, ge=1, le=500),
    scan_limit: int = Query(default=5000, ge=1, le=10000),
    service: QdrantService = Depends(get_qdrant_service),
) -> AssetListResponse:
    return service.list_assets(limit=limit, scan_limit=scan_limit)


@app.get("/api/metrics", response_model=MetricsResponse)
def metrics(
    scan_limit: int = Query(default=5000, ge=1, le=10000),
    service: QdrantService = Depends(get_qdrant_service),
) -> MetricsResponse:
    return service.metrics(scan_limit=scan_limit)
