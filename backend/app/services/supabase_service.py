from functools import lru_cache
from datetime import datetime, timezone
from typing import Any

from fastapi import HTTPException
import httpx

from app.config import Settings, get_settings
from app.models import (
    ConversationCreateRequest,
    ConversationResponse,
    CurateRecommendationRequest,
    CurateRecommendationResponse,
    DashboardSummaryResponse,
    FeedbackCreateRequest,
    FeedbackResponse,
    InsightResponse,
    InteractionSaveRequest,
    InteractionSaveResponse,
    ReviewFeedbackRequest,
    SupabaseHealthResponse,
    SupabaseTablesResponse,
)


APPLICATION_TABLES = [
    "conversations",
    "user_queries",
    "generated_responses",
    "retrieval_evidence",
    "recommendations",
    "user_feedback",
]

DASHBOARD_VIEWS = [
    "dashboard_popular_topics",
    "dashboard_evidence_usage",
    "dashboard_lecture_usage",
    "dashboard_feedback_summary",
    "dashboard_activity_summary",
]


class SupabaseService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        if not settings.supabase_url or not settings.supabase_secret_key:
            self.enabled = False
            self.base_url = ""
            self.headers: dict[str, str] = {}
            return

        self.enabled = True
        self.base_url = settings.supabase_url.rstrip("/")
        self.headers = {
            "apikey": settings.supabase_secret_key,
            "Authorization": f"Bearer {settings.supabase_secret_key}",
            "Content-Type": "application/json",
        }

    def health(self) -> SupabaseHealthResponse:
        if not self.enabled:
            return SupabaseHealthResponse(status="not_configured", configured=False)

        tables = self.list_tables().tables
        expected = APPLICATION_TABLES + DASHBOARD_VIEWS
        missing = [table for table in expected if table not in tables]
        return SupabaseHealthResponse(
            status="ok" if not missing else "schema_incomplete",
            configured=True,
            url=self.base_url,
            tables_found=tables,
            missing_tables=missing,
        )

    def list_tables(self) -> SupabaseTablesResponse:
        data = self._request("GET", "/rest/v1/")
        definitions = data.get("definitions", {}) if isinstance(data, dict) else {}
        return SupabaseTablesResponse(tables=sorted(definitions.keys()))

    def create_conversation(
        self, request: ConversationCreateRequest
    ) -> ConversationResponse:
        record = {
            "session_id": request.session_id,
            "title": request.title,
            "user_id": request.user_id,
            "metadata": request.metadata or {},
        }
        data = self._request(
            "POST",
            "/rest/v1/conversations",
            json=record,
            prefer="return=representation",
        )
        return ConversationResponse(**data[0])

    def list_conversations(self, limit: int) -> list[ConversationResponse]:
        data = self._request(
            "GET",
            f"/rest/v1/conversations?select=*&order=started_at.desc&limit={limit}",
        )
        return [ConversationResponse(**item) for item in data]

    def get_conversation_messages(self, conversation_id: str) -> list[dict[str, Any]]:
        data = self._request(
            "GET",
            f"/rest/v1/user_queries?conversation_id=eq.{conversation_id}&select=*,generated_responses(*,retrieval_evidence(*),recommendations(*))&order=created_at.asc",
        )
        return data if data else []

    def save_interaction(
        self, request: InteractionSaveRequest
    ) -> InteractionSaveResponse:
        query_id: str | None = None
        try:
            query = self._request(
                "POST",
                "/rest/v1/user_queries",
                json={
                    "conversation_id": request.conversation_id,
                    "query_text": request.query_text,
                    "normalized_topic": request.normalized_topic,
                    "detected_intent": request.detected_intent,
                    "metadata": request.metadata or {},
                },
                prefer="return=representation",
            )[0]
            query_id = query["query_id"]

            response = self._request(
                "POST",
                "/rest/v1/generated_responses",
                json={
                    "query_id": query_id,
                    "generated_answer": request.generated_answer,
                    "model_name": request.model_name,
                    "model_provider": request.model_provider,
                    "prompt_version": request.prompt_version,
                    "response_status": "completed",
                    "latency_ms": request.latency_ms,
                    "input_token_count": request.input_token_count,
                    "metadata": request.metadata or {},
                },
                prefer="return=representation",
            )[0]
            response_id = response["response_id"]

            evidence_records = []
            seen_qdrant_ids: set[str] = set()
            for rank, item in enumerate(request.evidence, start=1):
                payload = _evidence_payload(item, response_id, rank)
                qdrant_record_id = payload["qdrant_record_id"]
                if qdrant_record_id in seen_qdrant_ids:
                    continue
                seen_qdrant_ids.add(qdrant_record_id)
                evidence_records.append(payload)
            if evidence_records:
                self._request(
                    "POST",
                    "/rest/v1/retrieval_evidence",
                    json=evidence_records,
                    prefer="return=minimal",
                )

            recommendation_records: list[dict[str, Any]] = []

            self._request(
                "PATCH",
                f"/rest/v1/conversations?conversation_id=eq.{request.conversation_id}",
                json={"last_activity_at": datetime.now(timezone.utc).isoformat()},
                prefer="return=minimal",
            )

            return InteractionSaveResponse(
                conversation_id=request.conversation_id,
                query_id=query_id,
                response_id=response_id,
                evidence_count=len(evidence_records),
                recommendation_count=len(recommendation_records),
            )
        except Exception:
            if query_id:
                self._request(
                    "DELETE",
                    f"/rest/v1/user_queries?query_id=eq.{query_id}",
                    prefer="return=minimal",
                )
            raise

    def curate_recommendation(
        self, request: CurateRecommendationRequest
    ) -> CurateRecommendationResponse:
        rec_payload = {
            "response_id": request.insight_id,
            "recommendation_type": request.category,
            "recommendation_text": request.recommendation_text,
            "priority": request.priority,
            "metadata": {
                **request.metadata,
                "title": request.title,
                "curated_at": datetime.now(timezone.utc).isoformat(),
            },
        }
        result = self._request(
            "POST",
            "/rest/v1/recommendations",
            json=rec_payload,
            prefer="return=representation",
        )
        rec_id = result[0]["recommendation_id"] if result else "created"

        # Mark the response as pending review
        self._request(
            "PATCH",
            f"/rest/v1/generated_responses?response_id=eq.{request.insight_id}",
            json={"response_status": "pending"},
            prefer="return=minimal",
        )

        return CurateRecommendationResponse(
            recommendation_id=rec_id,
            insight_id=request.insight_id,
        )

    def list_curated_recommendations(self, limit: int = 12, offset: int = 0) -> list[dict[str, Any]]:
        return self._request(
            "GET",
            f"/rest/v1/recommendations?select=*,generated_responses(query_id,generated_answer,response_status,user_queries(query_text),retrieval_evidence(qdrant_record_id,content_type,evidence_text,similarity_score,retrieval_rank))&order=created_at.desc&limit={limit}&offset={offset}",
        )

    def save_feedback(self, request: FeedbackCreateRequest) -> FeedbackResponse:
        data = self._request(
            "POST",
            "/rest/v1/user_feedback",
            json={
                "response_id": request.response_id,
                "user_id": request.user_id,
                "rating": request.rating,
                "is_helpful": request.is_helpful,
                "approval": request.approval,
                "feedback_text": request.feedback_text,
            },
            prefer="return=representation",
        )
        return FeedbackResponse(**data[0])

    def save_review_feedback(self, request: ReviewFeedbackRequest) -> FeedbackResponse:
        response_id = request.response_id or request.insight_id
        if not response_id:
            raise HTTPException(
                status_code=422, detail="Either response_id or insight_id is required"
            )
        return self.save_feedback(
            FeedbackCreateRequest(
                response_id=response_id,
                user_id=request.user_id,
                rating=request.rating,
                is_helpful=request.is_helpful,
                approval=request.decision,
                feedback_text=request.notes,
            )
        )

    def get_insight(self, insight_id: str) -> InsightResponse:
        responses = self._request(
            "GET",
            f"/rest/v1/generated_responses?response_id=eq.{insight_id}&select=*",
        )
        if not responses:
            raise HTTPException(status_code=404, detail="Insight not found")

        response = responses[0]
        query = self._select_by_id(
            "user_queries",
            "query_id",
            response["query_id"],
        )
        evidence = self._request(
            "GET",
            f"/rest/v1/retrieval_evidence?response_id=eq.{insight_id}&select=*&order=retrieval_rank.asc",
        )
        recommendations = self._request(
            "GET",
            f"/rest/v1/recommendations?response_id=eq.{insight_id}&select=*&order=priority.asc",
        )
        feedback = self._request(
            "GET",
            f"/rest/v1/user_feedback?response_id=eq.{insight_id}&select=*&order=created_at.desc",
        )

        return InsightResponse(
            insight_id=insight_id,
            response=response,
            query=query,
            evidence=evidence,
            recommendations=recommendations,
            feedback=feedback,
        )

    def list_insights(self, limit: int, status: str | None = None) -> list[dict[str, Any]]:
        if status in {"pending", "completed", "failed", "blocked"}:
            return self._request(
                "GET",
                "/rest/v1/generated_responses"
                f"?select=*&order=created_at.desc&limit={limit}&response_status=eq.{status}",
            )

        responses = self._request(
            "GET",
            f"/rest/v1/generated_responses?select=*&order=created_at.desc&limit={limit}",
        )
        if not status:
            return responses
        return [
            response
            for response in responses
            if (response.get("metadata") or {}).get("status") == status
        ]

    def dashboard_summary(self) -> DashboardSummaryResponse:
        activity = self._select_first("dashboard_activity_summary")
        feedback = self._select_first("dashboard_feedback_summary")
        popular = self._select_many(
            "dashboard_popular_topics",
            "query_count.desc",
            10,
        )
        evidence = self._select_many(
            "dashboard_evidence_usage",
            "evidence_usage_count.desc",
            10,
        )
        lectures = self._select_many(
            "dashboard_lecture_usage",
            "evidence_usage_count.desc",
            10,
        )
        return DashboardSummaryResponse(
            activity_summary=activity,
            popular_topics=popular,
            evidence_usage=evidence,
            lecture_usage=lectures,
            feedback_summary=feedback,
        )

    def _select_first(self, table: str) -> dict[str, Any]:
        data = self._request("GET", f"/rest/v1/{table}?select=*&limit=1")
        return data[0] if data else {}

    def _select_by_id(self, table: str, key: str, value: str) -> dict[str, Any]:
        data = self._request("GET", f"/rest/v1/{table}?{key}=eq.{value}&select=*")
        return data[0] if data else {}

    def _select_many(self, table: str, order: str, limit: int) -> list[dict[str, Any]]:
        return self._request(
            "GET",
            f"/rest/v1/{table}?select=*&order={order}&limit={limit}",
        )

    def _request(
        self,
        method: str,
        path: str,
        *,
        json: Any | None = None,
        prefer: str | None = None,
    ) -> Any:
        if not self.enabled:
            raise HTTPException(status_code=500, detail="Supabase is not configured")

        headers = dict(self.headers)
        if prefer:
            headers["Prefer"] = prefer

        try:
            with httpx.Client(timeout=30) as client:
                response = client.request(
                    method,
                    f"{self.base_url}{path}",
                    headers=headers,
                    json=json,
                )
        except httpx.HTTPError as exc:
            raise HTTPException(
                status_code=502, detail=f"Supabase request failed: {exc}"
            ) from exc

        if response.status_code >= 400:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Supabase error: {response.text}",
            )

        if not response.content:
            return None
        return response.json()


def _evidence_payload(item: Any, response_id: str, rank: int) -> dict[str, Any]:
    metadata = item.metadata or {}
    qdrant_record_id = item.qdrant_record_id or item.point_id
    if not qdrant_record_id:
        raise HTTPException(status_code=422, detail="Evidence item needs a Qdrant ID")

    return {
        "response_id": response_id,
        "qdrant_record_id": qdrant_record_id,
        "content_type": item.content_type,
        "lecture_id": item.lecture_id,
        "module_id": item.module_id,
        "similarity_score": item.similarity_score
        if item.similarity_score is not None
        else item.score,
        "retrieval_rank": item.retrieval_rank or rank,
        "evidence_text": item.evidence_text or item.text,
        "asset_path": item.asset_path,
        "timestamp_seconds": item.timestamp_seconds,
        "metadata": metadata,
    }


@lru_cache
def get_supabase_service() -> SupabaseService:
    return SupabaseService(get_settings())
