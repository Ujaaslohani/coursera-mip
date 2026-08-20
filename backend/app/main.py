import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

from app.api import assets, processing_jobs, embeddings, query, synthesize, insights, review_feedback, metrics, audit_log, segments
from app.database.connection import Base, engine, ensure_vector_extension, ensure_new_columns
from app.database import models  # noqa: F401 — registers models on Base before create_all

ensure_vector_extension()
Base.metadata.create_all(bind=engine)
ensure_new_columns()

app = FastAPI(
    title="Coursera Multimodal Intelligence Platform — Backend",
    description="Ingestion, processing-job orchestration, retrieval, synthesis, and review APIs per product brief §7.3.",
    version="0.1.0",
)

_allowed_origins = os.environ.get("CORS_ALLOWED_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(assets.router, tags=["assets"])
app.include_router(processing_jobs.router, tags=["processing-jobs"])
app.include_router(embeddings.router, tags=["embeddings"])
app.include_router(query.router, tags=["query"])
app.include_router(synthesize.router, tags=["synthesize"])
app.include_router(insights.router, tags=["insights"])
app.include_router(review_feedback.router, tags=["review-feedback"])
app.include_router(metrics.router, tags=["metrics"])
app.include_router(audit_log.router, tags=["audit-log"])
app.include_router(segments.router, tags=["segments"])


@app.get("/health")
def health_check():
    return {"status": "ok"}
