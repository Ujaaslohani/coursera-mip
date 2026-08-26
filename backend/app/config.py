from functools import lru_cache
import os
from pathlib import Path

from dotenv import load_dotenv


BACKEND_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(BACKEND_ROOT / ".env")


class Settings:
    qdrant_url: str
    qdrant_collection: str
    qdrant_api_key: str | None
    embedding_model: str
    embedding_dimensions: int
    qdrant_distance: str
    hf_home: str
    frontend_origins: list[str]

    def __init__(self) -> None:
        self.qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333").strip()
        self.qdrant_collection = os.getenv(
            "QDRANT_COLLECTION", "COURSEERA_ALMAX_MULTIMODAL"
        ).strip()
        self.qdrant_api_key = (
            os.getenv("QDRANT_API_KEY")
            or os.getenv("BACKEND_KEY")
            or os.getenv("QDRANT_BACKEND_KEY")
        )
        self.embedding_model = os.getenv(
            "EMBEDDING_MODEL", "BAAI/bge-base-en-v1.5"
        ).strip()
        self.embedding_dimensions = int(os.getenv("EMBEDDING_DIMENSIONS", "768"))
        self.qdrant_distance = os.getenv("QDRANT_DISTANCE", "Cosine").strip()
        self.hf_home = os.getenv("HF_HOME", str(BACKEND_ROOT / ".cache" / "huggingface"))
        hf_home_path = Path(self.hf_home)
        if not hf_home_path.is_absolute():
            hf_home_path = BACKEND_ROOT / hf_home_path
        self.hf_home = str(hf_home_path)
        os.environ.setdefault("HF_HOME", self.hf_home)
        os.environ.setdefault("SENTENCE_TRANSFORMERS_HOME", str(hf_home_path / "sentence-transformers"))
        self.frontend_origins = [
            origin.strip()
            for origin in os.getenv(
                "FRONTEND_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000"
            ).split(",")
            if origin.strip()
        ]


@lru_cache
def get_settings() -> Settings:
    return Settings()
