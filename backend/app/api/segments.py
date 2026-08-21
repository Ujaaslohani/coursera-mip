from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.auth.dependencies import CurrentUser, require_role_permission
from app.services.segment_service import get_segment

router = APIRouter()


class SegmentResponse(BaseModel):
    segment_id: str
    asset_id: str
    modality: str
    text_content: str | None
    timestamp_start: float | None
    timestamp_end: float | None


@router.get("/api/segments/{segment_id}", response_model=SegmentResponse)
def get_segment_endpoint(
    segment_id: str,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(require_role_permission("insights:read")),
):
    """Retrieve one segment's content — used to preview what a citation
    actually says, rather than showing a bare, opaque segment_id. Gated on
    the same `insights:read` permission as viewing the insight that cites
    it (a reviewer who can see the insight can see its own evidence)."""
    segment = get_segment(db, segment_id)
    if segment is None:
        raise HTTPException(status_code=404, detail="Segment not found")
    return SegmentResponse(
        segment_id=segment.id,
        asset_id=segment.asset_id,
        modality=segment.modality.value,
        text_content=segment.text_content,
        timestamp_start=segment.timestamp_start,
        timestamp_end=segment.timestamp_end,
    )
