from functools import lru_cache
from typing import Any

from fastapi import HTTPException
from qdrant_client import QdrantClient
from qdrant_client.http.exceptions import UnexpectedResponse

from app.config import Settings, get_settings
from app.models import (
    AssetListResponse,
    AssetSummary,
    CollectionResponse,
    EmbeddingRefreshResponse,
    MetadataOptionsResponse,
    MetricsResponse,
    RecordResponse,
    ScrollResponse,
)


TEXT_PAYLOAD_KEYS = (
    "page_content",
    "text",
    "excerpt",
    "searchable_text",
    "caption_text",
    "transcript",
    "description",
    "summary",
    "thread_title",
    "post_text",
    "review_text",
    "question",
    "question_text",
    "explanation",
    "answer_text",
)


class QdrantService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.client = QdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key,
            timeout=60,
            check_compatibility=False,
        )

    def get_collection(self) -> CollectionResponse:
        try:
            collection = self.client.get_collection(self.settings.qdrant_collection)
        except UnexpectedResponse as exc:
            raise HTTPException(status_code=502, detail=str(exc)) from exc
        except Exception as exc:
            raise HTTPException(
                status_code=502, detail=f"Could not reach Qdrant: {exc}"
            ) from exc

        return CollectionResponse(
            collection_name=self.settings.qdrant_collection,
            status=str(getattr(collection, "status", None)),
            vectors_count=getattr(collection, "vectors_count", None),
            points_count=getattr(collection, "points_count", None),
            indexed_vectors_count=getattr(collection, "indexed_vectors_count", None),
            config=_model_dump(getattr(collection, "config", None)),
        )

    def scroll_records(self, limit: int, offset: str | None = None) -> ScrollResponse:
        try:
            points, next_offset = self.client.scroll(
                collection_name=self.settings.qdrant_collection,
                limit=limit,
                offset=offset,
                with_payload=True,
                with_vectors=False,
            )
        except Exception as exc:
            raise HTTPException(
                status_code=502, detail=f"Could not fetch Qdrant records: {exc}"
            ) from exc

        return ScrollResponse(
            records=[
                RecordResponse(id=str(point.id), payload=point.payload or {})
                for point in points
            ],
            next_page_offset=str(next_offset) if next_offset is not None else None,
        )

    def get_record(self, point_id: str) -> RecordResponse:
        try:
            points = self.client.retrieve(
                collection_name=self.settings.qdrant_collection,
                ids=[point_id],
                with_payload=True,
                with_vectors=False,
            )
        except Exception as exc:
            raise HTTPException(
                status_code=502, detail=f"Could not fetch Qdrant record: {exc}"
            ) from exc

        if not points:
            raise HTTPException(status_code=404, detail="Record not found")

        point = points[0]
        return RecordResponse(id=str(point.id), payload=point.payload or {})

    def verify_embeddings(self, point_ids: list[str]) -> EmbeddingRefreshResponse:
        unique_ids = [point_id for point_id in dict.fromkeys(point_ids) if point_id]
        if not unique_ids:
            return EmbeddingRefreshResponse(
                requested_count=0,
                verified_count=0,
                updated_count=0,
                skipped_count=0,
                status="no_segments_requested",
                details=[],
            )

        details: list[dict[str, Any]] = []
        verified_count = 0

        for point_id in unique_ids:
            try:
                record = self.get_record(point_id)
                payload = record.payload
                embedding_model = payload.get("embedding_model")
                dimensions = payload.get("embedding_dimensions")
                verified = embedding_model == self.settings.embedding_model
                if dimensions is not None:
                    verified = verified and int(dimensions) == self.settings.embedding_dimensions
                verified_count += 1 if verified else 0
                details.append(
                    {
                        "point_id": point_id,
                        "exists": True,
                        "verified": verified,
                        "embedding_model": embedding_model,
                        "embedding_dimensions": dimensions,
                        "message": "Existing Qdrant point verified; no vector mutation performed.",
                    }
                )
            except HTTPException as exc:
                details.append(
                    {
                        "point_id": point_id,
                        "exists": False,
                        "verified": False,
                        "message": exc.detail,
                    }
                )

        skipped_count = len(unique_ids) - verified_count
        return EmbeddingRefreshResponse(
            requested_count=len(unique_ids),
            verified_count=verified_count,
            updated_count=0,
            skipped_count=skipped_count,
            status="verified_existing_embeddings",
            details=details,
        )

    def metadata_options(self, scan_limit: int) -> MetadataOptionsResponse:
        records = self._scroll_payloads(scan_limit)
        return MetadataOptionsResponse(
            content_types=_sorted_unique(records, "content_type"),
            course_ids=_sorted_unique(records, "course_id"),
            lecture_ids=_sorted_unique(records, "lecture_id"),
            concept_tags=_sorted_unique(records, "concept_tags"),
            friction_types=_sorted_unique(records, "friction_type"),
            embedding_models=_sorted_unique(records, "embedding_model"),
            scanned_records=len(records),
        )

    def metrics(self, scan_limit: int) -> MetricsResponse:
        collection = self.get_collection()
        records = self._scroll_payloads(scan_limit)
        return MetricsResponse(
            collection_name=self.settings.qdrant_collection,
            qdrant_status=collection.status,
            points_count=collection.points_count,
            scanned_records=len(records),
            content_type_counts=_counts(records, "content_type"),
            course_id_counts=_counts(records, "course_id"),
            embedding_model_counts=_counts(records, "embedding_model"),
        )

    def list_assets(self, limit: int, scan_limit: int) -> AssetListResponse:
        records = self._scroll_records(scan_limit)
        grouped: dict[str, dict[str, Any]] = {}

        for record in records:
            payload = record.payload
            asset_id = _payload_str(payload, "asset_id") or _payload_str(
                payload, "source_id"
            )
            if not asset_id:
                continue

            item = grouped.setdefault(
                asset_id,
                {
                    "asset_id": asset_id,
                    "content_type": _payload_str(payload, "content_type"),
                    "course_id": _payload_str(payload, "course_id"),
                    "lecture_id": _payload_str(payload, "lecture_id"),
                    "segment_count": 0,
                    "sample_point_id": record.id,
                    "sample_text": _extract_text(payload),
                },
            )
            item["segment_count"] += 1
            item["content_type"] = item["content_type"] or _payload_str(
                payload, "content_type"
            )
            item["course_id"] = item["course_id"] or _payload_str(payload, "course_id")
            item["lecture_id"] = item["lecture_id"] or _payload_str(
                payload, "lecture_id"
            )
            if not item["sample_text"]:
                item["sample_text"] = _extract_text(payload)

        assets = [
            AssetSummary(**item)
            for item in sorted(
                grouped.values(),
                key=lambda value: (-value["segment_count"], value["asset_id"]),
            )[:limit]
        ]
        return AssetListResponse(assets=assets, scanned_records=len(records))

    def _scroll_records(self, scan_limit: int) -> list[RecordResponse]:
        records: list[RecordResponse] = []
        offset: Any = None

        while len(records) < scan_limit:
            batch_limit = min(256, scan_limit - len(records))
            try:
                points, offset = self.client.scroll(
                    collection_name=self.settings.qdrant_collection,
                    limit=batch_limit,
                    offset=offset,
                    with_payload=True,
                    with_vectors=False,
                )
            except Exception as exc:
                raise HTTPException(
                    status_code=502, detail=f"Could not scan Qdrant records: {exc}"
                ) from exc

            if not points:
                break

            records.extend(
                RecordResponse(id=str(point.id), payload=point.payload or {})
                for point in points
            )

            if offset is None:
                break

        return records

    def _scroll_payloads(self, scan_limit: int) -> list[dict[str, Any]]:
        return [record.payload for record in self._scroll_records(scan_limit)]


def _extract_text(payload: dict[str, Any]) -> str:
    for key in TEXT_PAYLOAD_KEYS:
        value = payload.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def _payload_str(payload: dict[str, Any], key: str) -> str | None:
    value = payload.get(key)
    if value is None:
        return None
    if isinstance(value, str):
        return value
    return str(value)


def _timestamp(payload: dict[str, Any]) -> str | None:
    if "timestamp" in payload:
        return _payload_str(payload, "timestamp")

    start = payload.get("start_seconds")
    end = payload.get("end_seconds")
    if start is not None and end is not None:
        return f"{start}-{end}s"
    if start is not None:
        return f"{start}s"
    return _payload_str(payload, "location")


def _iter_values(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value if item is not None and str(item).strip()]
    return [str(value)] if str(value).strip() else []


def _sorted_unique(records: list[dict[str, Any]], key: str) -> list[str]:
    values: set[str] = set()
    for record in records:
        values.update(_iter_values(record.get(key)))
    return sorted(values)


def _counts(records: list[dict[str, Any]], key: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for record in records:
        for value in _iter_values(record.get(key)):
            counts[value] = counts.get(value, 0) + 1
    return dict(sorted(counts.items(), key=lambda item: (-item[1], item[0])))


def _model_dump(value: Any) -> dict[str, Any]:
    if value is None:
        return {}
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json")
    if hasattr(value, "dict"):
        return value.dict()
    return {}


@lru_cache
def get_qdrant_service() -> QdrantService:
    return QdrantService(get_settings())
