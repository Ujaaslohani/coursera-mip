from typing import Any

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str
    qdrant_url_configured: bool
    qdrant_collection: str
    embedding_model: str


class CollectionResponse(BaseModel):
    collection_name: str
    status: str | None = None
    vectors_count: int | None = None
    points_count: int | None = None
    indexed_vectors_count: int | None = None
    config: dict[str, Any] = Field(default_factory=dict)


class RecordResponse(BaseModel):
    id: str
    payload: dict[str, Any] = Field(default_factory=dict)


class ScrollResponse(BaseModel):
    records: list[RecordResponse]
    next_page_offset: str | None = None


class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1)
    top_k: int = Field(default=5, ge=1, le=25)
    filters: dict[str, Any] = Field(default_factory=dict)


class EvidenceResult(BaseModel):
    id: str
    score: float | None = None
    text: str
    payload: dict[str, Any] = Field(default_factory=dict)


class QueryResponse(BaseModel):
    query: str
    top_k: int
    collection_name: str
    results: list[EvidenceResult]


class MetadataOptionsResponse(BaseModel):
    content_types: list[str] = Field(default_factory=list)
    course_ids: list[str] = Field(default_factory=list)
    lecture_ids: list[str] = Field(default_factory=list)
    concept_tags: list[str] = Field(default_factory=list)
    friction_types: list[str] = Field(default_factory=list)
    embedding_models: list[str] = Field(default_factory=list)
    scanned_records: int


class MetricsResponse(BaseModel):
    collection_name: str
    qdrant_status: str | None = None
    points_count: int | None = None
    scanned_records: int
    content_type_counts: dict[str, int] = Field(default_factory=dict)
    course_id_counts: dict[str, int] = Field(default_factory=dict)
    embedding_model_counts: dict[str, int] = Field(default_factory=dict)


class AssetSummary(BaseModel):
    asset_id: str
    content_type: str | None = None
    course_id: str | None = None
    lecture_id: str | None = None
    segment_count: int
    sample_point_id: str
    sample_text: str = ""


class AssetListResponse(BaseModel):
    assets: list[AssetSummary]
    scanned_records: int


class ContextRequest(BaseModel):
    query: str = Field(..., min_length=1)
    top_k: int = Field(default=5, ge=1, le=25)
    filters: dict[str, Any] = Field(default_factory=dict)


class EvidenceContext(BaseModel):
    point_id: str
    score: float | None = None
    source_id: str | None = None
    asset_id: str | None = None
    content_type: str | None = None
    course_id: str | None = None
    lecture_id: str | None = None
    timestamp: str | None = None
    text: str
    payload: dict[str, Any] = Field(default_factory=dict)


class ContextResponse(BaseModel):
    query: str
    evidence_count: int
    context: list[EvidenceContext]
