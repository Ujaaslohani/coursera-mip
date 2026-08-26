from typing import Any

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str
    qdrant_url_configured: bool
    qdrant_collection: str
    embedding_model: str
    supabase_configured: bool = False


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


class SupabaseHealthResponse(BaseModel):
    status: str
    configured: bool
    url: str | None = None
    tables_found: list[str] = Field(default_factory=list)
    missing_tables: list[str] = Field(default_factory=list)


class SupabaseTablesResponse(BaseModel):
    tables: list[str]


class ConversationCreateRequest(BaseModel):
    session_id: str = Field(..., min_length=1)
    title: str | None = None
    user_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class ConversationResponse(BaseModel):
    conversation_id: str
    session_id: str | None = None
    title: str | None = None
    user_id: str | None = None
    started_at: str | None = None
    last_activity_at: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class EvidenceSaveItem(BaseModel):
    qdrant_record_id: str | None = None
    point_id: str | None = None
    content_type: str
    lecture_id: str | None = None
    module_id: str | None = None
    similarity_score: float | None = None
    score: float | None = None
    retrieval_rank: int | None = None
    evidence_text: str | None = None
    text: str | None = None
    asset_path: str | None = None
    timestamp_seconds: float | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class RecommendationSaveItem(BaseModel):
    recommendation_type: str | None = None
    recommendation_text: str
    target_record_id: str | None = None
    priority: int | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class InteractionSaveRequest(BaseModel):
    conversation_id: str
    query_text: str = Field(..., min_length=1)
    generated_answer: str = Field(..., min_length=1)
    normalized_topic: str | None = None
    detected_intent: str | None = None
    model_name: str | None = None
    model_provider: str | None = None
    prompt_version: str | None = None
    latency_ms: int | None = Field(default=None, ge=0)
    input_token_count: int | None = Field(default=None, ge=0)
    evidence: list[EvidenceSaveItem] = Field(default_factory=list)
    recommendations: list[RecommendationSaveItem] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class InteractionSaveResponse(BaseModel):
    conversation_id: str
    query_id: str
    response_id: str
    evidence_count: int
    recommendation_count: int


class FeedbackCreateRequest(BaseModel):
    response_id: str
    user_id: str | None = None
    rating: int | None = Field(default=None, ge=1, le=5)
    is_helpful: bool | None = None
    approval: str | None = "pending"
    feedback_text: str | None = None


class FeedbackResponse(BaseModel):
    feedback_id: str
    response_id: str
    rating: int | None = None
    is_helpful: bool | None = None
    approval: str | None = None


class DashboardSummaryResponse(BaseModel):
    activity_summary: dict[str, Any] = Field(default_factory=dict)
    popular_topics: list[dict[str, Any]] = Field(default_factory=list)
    evidence_usage: list[dict[str, Any]] = Field(default_factory=list)
    lecture_usage: list[dict[str, Any]] = Field(default_factory=list)
    feedback_summary: dict[str, Any] = Field(default_factory=dict)


class AssetRegisterRequest(BaseModel):
    modality: str = Field(..., min_length=1)
    owner: str | None = None
    topic: str | None = None
    concept_tags: list[str] = Field(default_factory=list)
    storage_url: str = Field(..., min_length=1)
    permission_scope: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class AssetRegisterResponse(BaseModel):
    asset_id: str
    job_id: str
    status: str
    duplicate: bool = False


class RegisteredAsset(BaseModel):
    asset_id: str
    modality: str
    owner: str | None = None
    topic: str | None = None
    concept_tags: list[str] = Field(default_factory=list)
    storage_url: str
    permission_scope: list[str] = Field(default_factory=list)
    status: str
    created_at: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class ProcessingJobCreateRequest(BaseModel):
    asset_id: str


class ProcessingJobResponse(BaseModel):
    job_id: str
    asset_id: str
    stage: str
    error: str | None = None
    warnings: list[str] = Field(default_factory=list)
    created_at: str
    updated_at: str


class EmbeddingRefreshRequest(BaseModel):
    segment_ids: list[str] = Field(default_factory=list)
    qdrant_record_ids: list[str] = Field(default_factory=list)


class EmbeddingRefreshResponse(BaseModel):
    requested_count: int
    verified_count: int
    updated_count: int
    skipped_count: int
    status: str
    details: list[dict[str, Any]] = Field(default_factory=list)


class SynthesizeRequest(BaseModel):
    query: str = Field(..., min_length=1)
    conversation_id: str | None = None
    session_id: str | None = None
    retrieved_evidence: list[EvidenceContext] = Field(default_factory=list)
    top_k: int = Field(default=5, ge=1, le=25)
    filters: dict[str, Any] = Field(default_factory=dict)
    generated_answer: str | None = None
    model_name: str | None = "backend-extractive-synthesis"
    model_provider: str | None = "backend"
    recommendations: list[RecommendationSaveItem] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class Citation(BaseModel):
    point_id: str
    content_type: str | None = None
    lecture_id: str | None = None
    score: float | None = None
    text_preview: str = ""


class SynthesizeResponse(BaseModel):
    insight_id: str
    conversation_id: str
    query_id: str
    answer_text: str
    citations: list[Citation]
    confidence: float
    status: str = "pending_review"


class InsightResponse(BaseModel):
    insight_id: str
    response: dict[str, Any]
    query: dict[str, Any] = Field(default_factory=dict)
    evidence: list[dict[str, Any]] = Field(default_factory=list)
    recommendations: list[dict[str, Any]] = Field(default_factory=list)
    feedback: list[dict[str, Any]] = Field(default_factory=list)


class ReviewFeedbackRequest(BaseModel):
    insight_id: str | None = None
    response_id: str | None = None
    decision: str = Field(default="pending")
    notes: str | None = None
    rating: int | None = Field(default=None, ge=1, le=5)
    is_helpful: bool | None = None
    user_id: str | None = None
