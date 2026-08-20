"""ORM models for the multimodal pipeline, per doc §6.3 data assets and the
JSON Schemas in data/schemas/. Every table carries the source-lineage fields
(owner, topic, permission_scope / permitted checks downstream) required to
keep every synthesized insight traceable back to its evidence.

NOTE: the target Supabase database was already seeded by an earlier working
version of this codebase — native `uuid` id columns and Postgres enum types
`modalitytype` / `jobstage` already exist, with rows in every table. These
models match that existing physical schema exactly (native UUID ids, enum
type names without underscores) so Base.metadata.create_all() is a safe
no-op here, and a genuine CREATE on a fresh database (enum DDL is checkfirst
by default, so it works against both).
"""
import enum
import uuid
from datetime import datetime, timezone

from pgvector.sqlalchemy import Vector
from sqlalchemy import Column, DateTime, Enum as SAEnum, Float, ForeignKey, JSON, Text, Uuid

from app.database.connection import Base


def _uuid() -> str:
    return str(uuid.uuid4())


def _now() -> datetime:
    return datetime.now(timezone.utc)


class ModalityType(str, enum.Enum):
    video = "video"
    image = "image"
    slide = "slide"
    transcript = "transcript"
    quiz = "quiz"
    discussion = "discussion"


class JobStage(str, enum.Enum):
    """Full lifecycle per doc §4 (Engineering Lead): 'uploaded, preprocessed,
    embedded, indexed, searchable, retrieved, synthesized, reviewed, and
    archived.' `uploaded`..`searchable` progress during ingestion; `retrieved`,
    `synthesized`, and `reviewed` progress as THIS asset's own segments are
    used by a live query (see app.services.lifecycle_service) — an asset
    only reaches `reviewed` once evidence drawn from it was actually part of
    a reviewed insight, not merely indexed. `archived` is a manual, explicit
    action (see POST /api/processing-jobs/{id}/archive).
    """
    uploaded = "uploaded"
    preprocessed = "preprocessed"
    embedded = "embedded"
    indexed = "indexed"
    searchable = "searchable"
    retrieved = "retrieved"
    synthesized = "synthesized"
    reviewed = "reviewed"
    archived = "archived"
    failed = "failed"


# Forward progression order for lifecycle_service.advance_if_later — index
# position is the "how far along" ranking; `failed` is a terminal side-branch,
# not part of this ordering.
JOB_STAGE_PROGRESSION = [
    JobStage.uploaded,
    JobStage.preprocessed,
    JobStage.embedded,
    JobStage.indexed,
    JobStage.searchable,
    JobStage.retrieved,
    JobStage.synthesized,
    JobStage.reviewed,
    JobStage.archived,
]


class Asset(Base):
    __tablename__ = "assets"

    id = Column(Uuid(as_uuid=False), primary_key=True, default=_uuid)
    modality = Column(SAEnum(ModalityType, name="modalitytype"), nullable=False)
    owner = Column(Text, nullable=False)
    topic = Column(Text, nullable=True)
    concept_tags = Column(JSON, nullable=True, default=list)
    storage_url = Column(Text, nullable=False)
    permission_scope = Column(JSON, nullable=True, default=list)
    created_at = Column(DateTime, default=_now)


class ProcessingJob(Base):
    __tablename__ = "processing_jobs"

    id = Column(Uuid(as_uuid=False), primary_key=True, default=_uuid)
    asset_id = Column(Uuid(as_uuid=False), ForeignKey("assets.id"), nullable=False)
    stage = Column(SAEnum(JobStage, name="jobstage"), default=JobStage.uploaded)
    error = Column(Text, nullable=True)
    created_at = Column(DateTime, default=_now)
    updated_at = Column(DateTime, default=_now, onupdate=_now)


class Segment(Base):
    __tablename__ = "segments"

    id = Column(Uuid(as_uuid=False), primary_key=True, default=_uuid)
    asset_id = Column(Uuid(as_uuid=False), ForeignKey("assets.id"), nullable=False)
    job_id = Column(Uuid(as_uuid=False), ForeignKey("processing_jobs.id"), nullable=True)
    modality = Column(SAEnum(ModalityType, name="modalitytype"), nullable=False)
    text_content = Column(Text, nullable=True)
    timestamp_start = Column(Float, nullable=True)
    timestamp_end = Column(Float, nullable=True)
    embedding = Column(Vector(1536), nullable=True)  # matches ai/embeddings/embed.py EMBEDDING_MODEL dims
    image_embedding = Column(Vector(512), nullable=True)  # CLIP ViT-B/32 — see ai/embeddings/clip_embed.py
    segment_metadata = Column(JSON, nullable=True, default=dict)
    created_at = Column(DateTime, default=_now)


class Query(Base):
    __tablename__ = "queries"

    id = Column(Uuid(as_uuid=False), primary_key=True, default=_uuid)
    user_id = Column(Text, nullable=False)
    question_text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=_now)


class Insight(Base):
    __tablename__ = "insights"

    id = Column(Uuid(as_uuid=False), primary_key=True, default=_uuid)
    query_id = Column(Uuid(as_uuid=False), ForeignKey("queries.id"), nullable=False)
    answer_text = Column(Text, nullable=False)
    citations = Column(JSON, nullable=True, default=list)
    confidence = Column(Float, nullable=True)
    status = Column(Text, default="pending_review")  # pending_review|accept|edit|reject|escalate
    created_at = Column(DateTime, default=_now)


class ReviewFeedback(Base):
    __tablename__ = "review_feedback"

    id = Column(Uuid(as_uuid=False), primary_key=True, default=_uuid)
    insight_id = Column(Uuid(as_uuid=False), ForeignKey("insights.id"), nullable=False)
    reviewer_id = Column(Text, nullable=False)
    decision = Column(Text, nullable=False)  # accept | edit | reject | escalate
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=_now)


class AuditLog(Base):
    """Every mutating action and every access to sensitive data, per doc
    §5.4 'Security, Logging, and Observability': 'Every ingestion job,
    embedding job, query, retrieval call, model call, and export event must
    be logged' and §5.4 governance: 'audit-ready records.'
    """
    __tablename__ = "audit_log"

    id = Column(Uuid(as_uuid=False), primary_key=True, default=_uuid)
    actor = Column(Text, nullable=False)
    action = Column(Text, nullable=False)
    resource_type = Column(Text, nullable=True)
    resource_id = Column(Text, nullable=True)
    details = Column(JSON, nullable=True, default=dict)
    created_at = Column(DateTime, default=_now)
