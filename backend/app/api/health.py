from fastapi import APIRouter, Depends

from app.config import Settings, get_settings
from app.models import HealthResponse


router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health(config: Settings = Depends(get_settings)) -> HealthResponse:
    return HealthResponse(
        status="ok",
        qdrant_url_configured=bool(config.qdrant_url),
        qdrant_collection=config.qdrant_collection,
        embedding_model=config.embedding_model,
        supabase_configured=bool(config.supabase_url and config.supabase_secret_key),
    )
