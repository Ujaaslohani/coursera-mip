from functools import lru_cache
import builtins
import os
from pathlib import Path
import sys
from typing import Any

from fastapi import HTTPException

from app.config import Settings, get_settings
from app.models import (
    Citation,
    ContextResponse,
    EvidenceContext,
    EvidenceResult,
    EvidenceSaveItem,
    QueryResponse,
    RecommendationSaveItem,
    SynthesizeRequest,
    SynthesizeResponse,
)


class RagService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.backend_root = Path(__file__).resolve().parents[2]
        self._pipeline = None
        self._synthesize_insight = None

    def retrieve(self, query: str, top_k: int) -> QueryResponse:
        chunks = self.retrieve_chunks(query=query, top_k=top_k)
        return QueryResponse(
            query=query,
            top_k=top_k,
            collection_name=self.settings.qdrant_collection,
            results=[
                EvidenceResult(
                    id=str(chunk["segment_id"]),
                    score=float(chunk.get("score", 0.0)),
                    text=str(chunk.get("excerpt", "")),
                    payload={
                        "source_id": chunk.get("source_id"),
                        "content_type": _content_type(chunk.get("modality")),
                        "timestamp": chunk.get("timestamp"),
                    },
                )
                for chunk in chunks
            ],
        )

    def context(self, query: str, top_k: int) -> ContextResponse:
        chunks = self.retrieve_chunks(query=query, top_k=top_k)
        context = [self._chunk_to_context(chunk) for chunk in chunks]
        return ContextResponse(query=query, evidence_count=len(context), context=context)

    def synthesize(self, request: SynthesizeRequest) -> tuple[SynthesizeResponse, list[EvidenceSaveItem], list[RecommendationSaveItem], str]:
        chunks = (
            [self._context_to_chunk(item) for item in request.retrieved_evidence]
            if request.retrieved_evidence
            else self.retrieve_chunks(query=request.query, top_k=request.top_k)
        )

        synthesize_insight = self._load_synthesis()
        try:
            insight = synthesize_insight(query=request.query, reranked_chunks=chunks)
        except Exception as exc:
            raise HTTPException(
                status_code=503,
                detail=f"RAG synthesis failed: {exc}",
            ) from exc

        answer_text = (
            f"Summary: {insight.summary}\n\n"
            f"Friction Diagnostic:\n{insight.friction_explanation}\n\n"
            f"Recommended Action:\n{insight.recommended_action}"
        )
        citations = [
            Citation(
                point_id=item.segment_id,
                content_type=item.modality,
                lecture_id=item.source_id,
                score=item.confidence,
                text_preview=_preview(item.excerpt, 180),
            )
            for item in insight.evidence
        ]
        context_items = [self._chunk_to_context(chunk) for chunk in chunks]
        evidence = [self._context_to_evidence(item, rank) for rank, item in enumerate(context_items, start=1)]
        recommendations = [
            RecommendationSaveItem(
                recommendation_type="rag_synthesis",
                recommendation_text=insight.recommended_action,
                target_record_id=citations[0].point_id if citations else None,
                priority=1,
                metadata={"source": "rag.synthesis"},
            )
        ]

        return (
            SynthesizeResponse(
                insight_id=insight.insight_id,
                conversation_id="",
                query_id="",
                answer_text=answer_text,
                recommended_action=insight.recommended_action,
                citations=citations,
                confidence=round(float(insight.confidence), 3),
                status="completed",
            ),
            evidence,
            recommendations,
            answer_text,
        )

    def retrieve_chunks(self, query: str, top_k: int) -> list[dict[str, Any]]:
        pipeline = self._load_pipeline()
        try:
            return pipeline.retrieve_and_rerank(query=query, top_k=top_k)
        except Exception as exc:
            raise HTTPException(
                status_code=503,
                detail=f"RAG retrieval failed: {exc}",
            ) from exc

    def _load_pipeline(self) -> Any:
        if self._pipeline is not None:
            return self._pipeline

        self._prepare_rag_imports()
        try:
            from rag.retreival import pipeline
        except Exception as exc:
            raise HTTPException(
                status_code=503,
                detail=f"Could not import rag retrieval pipeline: {exc}",
            ) from exc

        self._pipeline = pipeline
        return self._pipeline

    def _load_synthesis(self) -> Any:
        self._assert_env("GROQ_API_KEY", "RAG LLM synthesis")
        if self._synthesize_insight is not None:
            return self._synthesize_insight

        self._prepare_rag_imports()
        try:
            from rag.synthesis import synthesize_insight
        except Exception as exc:
            raise HTTPException(
                status_code=503,
                detail=f"Could not import rag synthesis: {exc}",
            ) from exc

        self._synthesize_insight = synthesize_insight
        return self._synthesize_insight

    def _prepare_rag_imports(self) -> None:
        if str(self.backend_root) not in sys.path:
            sys.path.insert(0, str(self.backend_root))
        # rag.retreival currently references os without importing it.
        if not hasattr(builtins, "os"):
            builtins.os = os

    def _assert_env(self, name: str, purpose: str) -> None:
        if not os.getenv(name):
            raise HTTPException(
                status_code=503,
                detail=f"{name} is required for {purpose}. Add it to backend/.env.",
            )

    def _chunk_to_context(self, chunk: dict[str, Any]) -> EvidenceContext:
        return EvidenceContext(
            point_id=str(chunk.get("segment_id", "")),
            score=float(chunk.get("score", 0.0)),
            source_id=_optional_str(chunk.get("source_id")),
            asset_id=_optional_str(chunk.get("source_id")),
            content_type=_content_type(chunk.get("modality")),
            lecture_id=_optional_str(chunk.get("source_id")),
            timestamp=_optional_str(chunk.get("timestamp")),
            text=str(chunk.get("excerpt", "")),
            payload={
                "source_id": chunk.get("source_id"),
                "content_type": _content_type(chunk.get("modality")),
                "timestamp": chunk.get("timestamp"),
            },
        )

    def _context_to_chunk(self, item: EvidenceContext) -> dict[str, Any]:
        return {
            "segment_id": item.point_id,
            "source_id": item.source_id or item.asset_id or item.lecture_id or item.point_id,
            "modality": item.content_type or "text",
            "timestamp": item.timestamp or "",
            "excerpt": item.text,
            "score": item.score or 0.0,
        }

    def _context_to_evidence(self, item: EvidenceContext, rank: int) -> EvidenceSaveItem:
        return EvidenceSaveItem(
            point_id=item.point_id,
            content_type=_content_type(item.content_type),
            lecture_id=item.lecture_id,
            module_id=_optional_str((item.payload or {}).get("module_id")),
            score=item.score,
            retrieval_rank=rank,
            text=item.text,
            asset_path=_optional_str((item.payload or {}).get("asset_path")),
            timestamp_seconds=_timestamp_seconds(item.payload or {}),
            metadata={
                "source_id": item.source_id,
                "asset_id": item.asset_id,
                "course_id": item.course_id,
                "provider": "rag",
            },
        )


def _preview(value: str, limit: int) -> str:
    text = " ".join((value or "").split())
    if len(text) <= limit:
        return text
    return text[: limit - 3].rstrip() + "..."


def _optional_str(value: Any) -> str | None:
    if value is None:
        return None
    return str(value)


def _content_type(value: Any) -> str:
    allowed = {"caption", "slide", "frame", "transcript", "quiz", "discussion"}
    content_type = str(value) if value is not None else ""
    return content_type if content_type in allowed else "caption"


def _timestamp_seconds(payload: dict[str, Any]) -> float | None:
    value = payload.get("timestamp_seconds") or payload.get("start_seconds")
    try:
        return float(value) if value is not None else None
    except (TypeError, ValueError):
        return None


@lru_cache
def get_rag_service() -> RagService:
    return RagService(get_settings())
