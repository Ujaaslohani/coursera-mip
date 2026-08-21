from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.auth.dependencies import CurrentUser, require_role_permission
from app.services.embedding_service import refresh_embeddings
from app.services.audit_service import log_action

router = APIRouter()


class EmbeddingRefreshRequest(BaseModel):
    segment_ids: list[str]


class EmbeddingRefreshResponse(BaseModel):
    updated_count: int


@router.post("/api/embeddings", response_model=EmbeddingRefreshResponse)
def generate_embeddings(
    payload: EmbeddingRefreshRequest,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(require_role_permission("processing:write")),
):
    """Generate or refresh embeddings for approved asset segments."""
    updated = refresh_embeddings(db, payload.segment_ids)
    log_action(db, actor=user.user_id, action="embeddings.refresh", resource_type="segment",
               details={"segment_ids": payload.segment_ids, "updated_count": updated})
    return EmbeddingRefreshResponse(updated_count=updated)
