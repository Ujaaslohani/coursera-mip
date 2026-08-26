from fastapi import Depends, FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

from app.config import Settings, get_settings
from app.models import (
    AssetRegisterRequest,
    AssetRegisterResponse,
    AssetListResponse,
    CollectionResponse,
    ContextRequest,
    ContextResponse,
    ConversationCreateRequest,
    ConversationResponse,
    DashboardSummaryResponse,
    EmbeddingRefreshRequest,
    EmbeddingRefreshResponse,
    FeedbackCreateRequest,
    FeedbackResponse,
    HealthResponse,
    InsightResponse,
    InteractionSaveRequest,
    InteractionSaveResponse,
    MetadataOptionsResponse,
    MetricsResponse,
    ProcessingJobCreateRequest,
    ProcessingJobResponse,
    QueryRequest,
    QueryResponse,
    RecordResponse,
    RegisteredAsset,
    ReviewFeedbackRequest,
    ScrollResponse,
    SynthesizeRequest,
    SynthesizeResponse,
    SupabaseHealthResponse,
    SupabaseTablesResponse,
)
from app.services.operations_store import OperationsStore, get_operations_store
from app.services.qdrant_service import QdrantService, get_qdrant_service
from app.services.supabase_service import SupabaseService, get_supabase_service
from app.services.synthesis_service import (
    build_answer,
    build_citations,
    context_from_evidence,
    estimate_confidence,
    evidence_for_supabase,
    recommendations_for_supabase,
)


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
        supabase_configured=bool(config.supabase_url and config.supabase_secret_key),
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


@app.get("/api/segments/{segment_id}", response_model=RecordResponse)
def segment(
    segment_id: str,
    service: QdrantService = Depends(get_qdrant_service),
) -> RecordResponse:
    return service.get_record(segment_id)


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


@app.post("/api/assets", response_model=AssetRegisterResponse)
def register_asset(
    request: AssetRegisterRequest,
    store: OperationsStore = Depends(get_operations_store),
) -> AssetRegisterResponse:
    return store.register_asset(request)


@app.get("/api/assets/registered", response_model=list[RegisteredAsset])
def registered_assets(
    store: OperationsStore = Depends(get_operations_store),
) -> list[RegisteredAsset]:
    return store.list_registered_assets()


@app.post("/api/processing-jobs", response_model=ProcessingJobResponse)
def start_processing_job(
    request: ProcessingJobCreateRequest,
    store: OperationsStore = Depends(get_operations_store),
) -> ProcessingJobResponse:
    return store.start_processing_job(request.asset_id)


@app.get("/api/processing-jobs/{job_id}", response_model=ProcessingJobResponse)
def processing_job(
    job_id: str,
    store: OperationsStore = Depends(get_operations_store),
) -> ProcessingJobResponse:
    return store.get_job(job_id)


@app.post("/api/processing-jobs/{job_id}/archive", response_model=ProcessingJobResponse)
def archive_processing_job(
    job_id: str,
    store: OperationsStore = Depends(get_operations_store),
) -> ProcessingJobResponse:
    return store.archive_job(job_id)


@app.post("/api/embeddings", response_model=EmbeddingRefreshResponse)
def refresh_embeddings(
    request: EmbeddingRefreshRequest,
    service: QdrantService = Depends(get_qdrant_service),
) -> EmbeddingRefreshResponse:
    point_ids = request.segment_ids + request.qdrant_record_ids
    return service.verify_embeddings(point_ids)


@app.get("/api/metrics", response_model=MetricsResponse)
def metrics(
    scan_limit: int = Query(default=5000, ge=1, le=10000),
    service: QdrantService = Depends(get_qdrant_service),
) -> MetricsResponse:
    return service.metrics(scan_limit=scan_limit)


@app.get("/api/supabase/health", response_model=SupabaseHealthResponse)
def supabase_health(
    service: SupabaseService = Depends(get_supabase_service),
) -> SupabaseHealthResponse:
    return service.health()


@app.get("/api/supabase/tables", response_model=SupabaseTablesResponse)
def supabase_tables(
    service: SupabaseService = Depends(get_supabase_service),
) -> SupabaseTablesResponse:
    return service.list_tables()


@app.post("/api/conversations", response_model=ConversationResponse)
def create_conversation(
    request: ConversationCreateRequest,
    service: SupabaseService = Depends(get_supabase_service),
) -> ConversationResponse:
    return service.create_conversation(request)


@app.get("/api/conversations", response_model=list[ConversationResponse])
def conversations(
    limit: int = Query(default=20, ge=1, le=100),
    service: SupabaseService = Depends(get_supabase_service),
) -> list[ConversationResponse]:
    return service.list_conversations(limit=limit)


@app.post("/api/interactions", response_model=InteractionSaveResponse)
def save_interaction(
    request: InteractionSaveRequest,
    service: SupabaseService = Depends(get_supabase_service),
) -> InteractionSaveResponse:
    return service.save_interaction(request)


@app.post("/api/feedback", response_model=FeedbackResponse)
def save_feedback(
    request: FeedbackCreateRequest,
    service: SupabaseService = Depends(get_supabase_service),
) -> FeedbackResponse:
    return service.save_feedback(request)


@app.post("/api/synthesize", response_model=SynthesizeResponse)
def synthesize(
    request: SynthesizeRequest,
    qdrant_service: QdrantService = Depends(get_qdrant_service),
    supabase_service: SupabaseService = Depends(get_supabase_service),
) -> SynthesizeResponse:
    if request.retrieved_evidence:
        context_response = context_from_evidence(request.query, request.retrieved_evidence)
    else:
        context_response = qdrant_service.build_context(
            query=request.query,
            top_k=request.top_k,
            filters=request.filters,
        )

    conversation_id = request.conversation_id
    if not conversation_id:
        conversation = supabase_service.create_conversation(
            ConversationCreateRequest(
                session_id=request.session_id or f"synthesize:{request.query[:64]}",
                title=request.query[:80],
                metadata={"created_by": "api_synthesize"},
            )
        )
        conversation_id = conversation.conversation_id

    answer_text = build_answer(request, context_response)
    saved = supabase_service.save_interaction(
        InteractionSaveRequest(
            conversation_id=conversation_id,
            query_text=request.query,
            generated_answer=answer_text,
            normalized_topic=request.metadata.get("normalized_topic"),
            detected_intent=request.metadata.get("detected_intent", "synthesis"),
            model_name=request.model_name,
            model_provider=request.model_provider,
            prompt_version=request.metadata.get("prompt_version"),
            evidence=evidence_for_supabase(context_response),
            recommendations=recommendations_for_supabase(request, context_response),
            metadata={
                **(request.metadata or {}),
                "status": "pending_review",
                "synthesis_mode": "extractive" if not request.generated_answer else "external_llm",
            },
        )
    )

    return SynthesizeResponse(
        insight_id=saved.response_id,
        conversation_id=saved.conversation_id,
        query_id=saved.query_id,
        answer_text=answer_text,
        citations=build_citations(context_response),
        confidence=estimate_confidence(context_response),
        status="pending_review",
    )


@app.get("/api/insights", response_model=list[dict])
def insights(
    status: str | None = None,
    limit: int = Query(default=50, ge=1, le=100),
    service: SupabaseService = Depends(get_supabase_service),
) -> list[dict]:
    return service.list_insights(limit=limit, status=status)


@app.get("/api/insights/{insight_id}", response_model=InsightResponse)
def insight(
    insight_id: str,
    service: SupabaseService = Depends(get_supabase_service),
) -> InsightResponse:
    return service.get_insight(insight_id)


@app.post("/api/review-feedback", response_model=FeedbackResponse)
def review_feedback(
    request: ReviewFeedbackRequest,
    service: SupabaseService = Depends(get_supabase_service),
) -> FeedbackResponse:
    return service.save_review_feedback(request)


@app.get("/api/dashboard/summary", response_model=DashboardSummaryResponse)
def dashboard_summary(
    service: SupabaseService = Depends(get_supabase_service),
) -> DashboardSummaryResponse:
    return service.dashboard_summary()
