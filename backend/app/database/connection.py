"""Database engine/session setup, per doc §6.3: relational data layer for
asset, job, segment, query, and insight records (Postgres + pgvector).
"""
import os

from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.environ["DATABASE_URL"]

engine = create_engine(DATABASE_URL, pool_pre_ping=True, connect_args={"sslmode": "require"})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def ensure_vector_extension() -> None:
    """Segment.embedding uses pgvector's Vector type — the extension must
    exist before Base.metadata.create_all() can create that column."""
    with engine.begin() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))


def ensure_new_columns() -> None:
    """Base.metadata.create_all() only creates MISSING tables — it never
    alters an existing one. `segments` already existed in this database
    before `image_embedding` (CLIP, 512-dim) was added to the model, so that
    column needs an explicit, idempotent ALTER TABLE. Call this AFTER
    create_all() — Postgres's `ADD COLUMN IF NOT EXISTS` is then safe to run
    on every startup against both this pre-existing database (where the
    column is genuinely missing) and a fresh one (where create_all already
    created it, making this a no-op)."""
    with engine.begin() as conn:
        conn.execute(text("ALTER TABLE segments ADD COLUMN IF NOT EXISTS image_embedding vector(512)"))
        conn.execute(text("ALTER TABLE segments ADD COLUMN IF NOT EXISTS job_id uuid"))


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
