from fastapi import APIRouter, Depends, Query

from app.models import (
    AssetListResponse,
    AssetRegisterRequest,
    AssetRegisterResponse,
    RegisteredAsset,
)
from app.services.operations_store import OperationsStore, get_operations_store
from app.services.qdrant_service import QdrantService, get_qdrant_service


router = APIRouter(prefix="/api/assets", tags=["assets"])


@router.get("", response_model=AssetListResponse)
def assets(
    limit: int = Query(default=50, ge=1, le=500),
    scan_limit: int = Query(default=5000, ge=1, le=10000),
    service: QdrantService = Depends(get_qdrant_service),
) -> AssetListResponse:
    return service.list_assets(limit=limit, scan_limit=scan_limit)


@router.post("", response_model=AssetRegisterResponse)
def register_asset(
    request: AssetRegisterRequest,
    store: OperationsStore = Depends(get_operations_store),
) -> AssetRegisterResponse:
    return store.register_asset(request)


@router.get("/registered", response_model=list[RegisteredAsset])
def registered_assets(
    store: OperationsStore = Depends(get_operations_store),
) -> list[RegisteredAsset]:
    return store.list_registered_assets()
