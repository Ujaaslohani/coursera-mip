from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import assets, conversations, health, jobs, qdrant, rag, supabase
from app.config import get_settings


settings = get_settings()

app = FastAPI(
    title="Coursera Multimodal Intelligence Backend",
    description="Backend API for RAG2 retrieval/synthesis orchestration and persistence.",
    version="0.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.frontend_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(qdrant.router)
app.include_router(assets.router)
app.include_router(jobs.router)
app.include_router(supabase.router)
app.include_router(conversations.router)
app.include_router(rag.router)
