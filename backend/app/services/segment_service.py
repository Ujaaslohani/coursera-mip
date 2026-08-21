from sqlalchemy.orm import Session

from app.database.models import Segment

# Backs GET /api/segments/{id} — lets the Recommendation Workspace show what
# a citation's segment_id actually says, instead of a bare, opaque UUID.


def get_segment(db: Session, segment_id: str) -> Segment | None:
    return db.query(Segment).filter(Segment.id == segment_id).first()
