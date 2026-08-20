from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.auth.dependencies import CurrentUser, require_role_permission
from app.services.asset_service import register_asset, list_assets_with_status
from app.services.audit_service import log_action
from app.services.storage_service import get_storage_backend

router = APIRouter()


class AssetCreateRequest(BaseModel):
    modality: str  # video | image | slide | transcript | quiz | discussion
    owner: str
    topic: str | None = None
    concept_tags: list[str] = []
    storage_url: str
    permission_scope: list[str] = []


class AssetCreateResponse(BaseModel):
    asset_id: str
    job_id: str
    status: str = "uploaded"
    duplicate: bool = False


class AssetStatusItem(BaseModel):
    asset_id: str
    modality: str
    owner: str
    topic: str | None
    job_id: str | None
    stage: str | None  # None means an asset row exists with no job at all (shouldn't normally happen)
    created_at: str | None


@router.post("/api/assets", response_model=AssetCreateResponse)
def create_asset(
    payload: AssetCreateRequest,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(require_role_permission("assets:write")),
):
    """Register a new video, image, slide, transcript, quiz, or discussion asset.
    Re-registering the same owner+modality+storage_url returns the existing
    asset instead of creating a duplicate (doc §5.4 duplicate-asset detection).
    Requires the `assets:write` permission (content-team/admin roles)."""
    asset, job_id, is_duplicate = register_asset(
        db,
        modality=payload.modality,
        owner=payload.owner,
        topic=payload.topic,
        concept_tags=payload.concept_tags,
        storage_url=payload.storage_url,
        permission_scope=payload.permission_scope,
    )
    log_action(db, actor=user.user_id, action="asset.register", resource_type="asset", resource_id=asset.id,
               details={"modality": payload.modality, "owner": payload.owner, "duplicate": is_duplicate})
    return AssetCreateResponse(
        asset_id=asset.id,
        job_id=job_id,
        status="duplicate" if is_duplicate else "uploaded",
        duplicate=is_duplicate,
    )


class StorageCheckResponse(BaseModel):
    storage_url: str
    exists: bool


@router.get("/api/assets/check-storage", response_model=StorageCheckResponse)
def check_storage(
    storage_url: str,
    user: CurrentUser = Depends(require_role_permission("assets:write")),
):
    """Lightweight pre-flight check so the Asset Intake form can warn about a
    typo'd path before registering an asset that will just fail at
    processing time. Same `assets:write` permission as registration itself."""
    exists = get_storage_backend().exists(storage_url)
    return StorageCheckResponse(storage_url=storage_url, exists=exists)


@router.get("/api/assets", response_model=list[AssetStatusItem])
def list_assets(
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(require_role_permission("processing:write")),
):
    """Every asset with its most recent processing stage — backs the
    Processing Monitor's processed/unprocessed list."""
    return list_assets_with_status(db)
