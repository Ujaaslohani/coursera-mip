from datetime import datetime, timezone
from functools import lru_cache
import json
from pathlib import Path
import threading
import uuid

from fastapi import HTTPException

from app.config import BACKEND_ROOT
from app.models import (
    AssetRegisterRequest,
    AssetRegisterResponse,
    ProcessingJobResponse,
    RegisteredAsset,
)


LIFECYCLE_STAGES = [
    "uploaded",
    "preprocessed",
    "embedded",
    "indexed",
    "searchable",
    "retrieved",
    "synthesized",
    "reviewed",
    "archived",
    "failed",
]


class OperationsStore:
    def __init__(self) -> None:
        self.path = BACKEND_ROOT / ".data" / "operations.json"
        self._lock = threading.Lock()
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def register_asset(self, request: AssetRegisterRequest) -> AssetRegisterResponse:
        with self._lock:
            state = self._load()
            duplicate_asset = self._find_duplicate(state, request)
            if duplicate_asset:
                job_id = duplicate_asset.get("initial_job_id") or self._create_job(
                    state,
                    duplicate_asset["asset_id"],
                    stage=duplicate_asset.get("status", "uploaded"),
                )["job_id"]
                duplicate_asset["initial_job_id"] = job_id
                self._save(state)
                return AssetRegisterResponse(
                    asset_id=duplicate_asset["asset_id"],
                    job_id=job_id,
                    status=duplicate_asset.get("status", "uploaded"),
                    duplicate=True,
                )

            asset_id = str(uuid.uuid4())
            now = _now()
            asset = {
                "asset_id": asset_id,
                "modality": request.modality,
                "owner": request.owner,
                "topic": request.topic,
                "concept_tags": request.concept_tags,
                "storage_url": request.storage_url,
                "permission_scope": request.permission_scope,
                "status": "uploaded",
                "created_at": now,
                "metadata": request.metadata or {},
            }
            state["assets"][asset_id] = asset
            job = self._create_job(state, asset_id, stage="uploaded")
            asset["initial_job_id"] = job["job_id"]
            self._save(state)
            return AssetRegisterResponse(
                asset_id=asset_id,
                job_id=job["job_id"],
                status="uploaded",
                duplicate=False,
            )

    def list_registered_assets(self) -> list[RegisteredAsset]:
        state = self._load()
        return [
            RegisteredAsset(**{k: v for k, v in asset.items() if k != "initial_job_id"})
            for asset in sorted(
                state["assets"].values(),
                key=lambda item: item.get("created_at", ""),
                reverse=True,
            )
        ]

    def start_processing_job(self, asset_id: str) -> ProcessingJobResponse:
        with self._lock:
            state = self._load()
            if asset_id not in state["assets"]:
                raise HTTPException(status_code=404, detail="Asset not found")

            warnings = [
                "Backend records lifecycle state only; media preprocessing is handled by the database/AI pipeline."
            ]
            job = self._create_job(
                state,
                asset_id,
                stage="searchable",
                warnings=warnings,
            )
            state["assets"][asset_id]["status"] = "searchable"
            self._save(state)
            return ProcessingJobResponse(**job)

    def get_job(self, job_id: str) -> ProcessingJobResponse:
        state = self._load()
        job = state["jobs"].get(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Processing job not found")
        return ProcessingJobResponse(**job)

    def archive_job(self, job_id: str) -> ProcessingJobResponse:
        with self._lock:
            state = self._load()
            job = state["jobs"].get(job_id)
            if not job:
                raise HTTPException(status_code=404, detail="Processing job not found")
            job["stage"] = "archived"
            job["updated_at"] = _now()
            self._save(state)
            return ProcessingJobResponse(**job)

    def _create_job(
        self,
        state: dict,
        asset_id: str,
        *,
        stage: str,
        error: str | None = None,
        warnings: list[str] | None = None,
    ) -> dict:
        if stage not in LIFECYCLE_STAGES:
            raise ValueError(f"Invalid job stage: {stage}")
        now = _now()
        job_id = str(uuid.uuid4())
        job = {
            "job_id": job_id,
            "asset_id": asset_id,
            "stage": stage,
            "error": error,
            "warnings": warnings or [],
            "created_at": now,
            "updated_at": now,
        }
        state["jobs"][job_id] = job
        return job

    def _find_duplicate(
        self, state: dict, request: AssetRegisterRequest
    ) -> dict | None:
        for asset in state["assets"].values():
            if (
                asset.get("owner") == request.owner
                and asset.get("modality") == request.modality
                and asset.get("storage_url") == request.storage_url
            ):
                return asset
        return None

    def _load(self) -> dict:
        if not self.path.exists():
            return {"assets": {}, "jobs": {}}
        with self.path.open("r", encoding="utf-8") as file:
            data = json.load(file)
        data.setdefault("assets", {})
        data.setdefault("jobs", {})
        return data

    def _save(self, state: dict) -> None:
        tmp_path = self.path.with_suffix(".tmp")
        with tmp_path.open("w", encoding="utf-8") as file:
            json.dump(state, file, indent=2)
        tmp_path.replace(self.path)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@lru_cache
def get_operations_store() -> OperationsStore:
    return OperationsStore()
