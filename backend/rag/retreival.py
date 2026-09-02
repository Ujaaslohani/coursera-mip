# Retrieval of relevant documents from Database using Vector Search and Cohere Reranking
import os
from typing import Any, List
from dotenv import load_dotenv

from qdrant_client import QdrantClient
from langchain_qdrant import QdrantVectorStore
from langchain_huggingface import HuggingFaceEndpointEmbeddings
from langchain_cohere import CohereRerank
from langchain_core.documents import Document

load_dotenv()


class RetrievalPipeline:
    def __init__(self, collection_name: str = "COURSEERA_ALMAX_MULTIMODAL"):
        self.collection_name = collection_name
        self.qdrant_url = os.getenv("QDRANT_URL")
        self.qdrant_api_key = (
            os.getenv("QDRANT_API_KEY")
            or os.getenv("BACKEND_KEY")
            or os.getenv("QDRANT_BACKEND_KEY")
        )

        # Serverless Cloud API (Uses ~0 MB server RAM)
        hf_token = (
            os.getenv("HF_TOKEN_EMBEDDING")
            or os.getenv("HF_TOKEN_ORIGINAL")
            or os.getenv("HF_TOKEN")
            or os.getenv("HUGGINGFACEHUB_API_TOKEN")
        )
        self.embeddings = HuggingFaceEndpointEmbeddings(
            model="BAAI/bge-base-en-v1.5",
            huggingfacehub_api_token=hf_token,
        )
        self.client = QdrantClient(
            url=self.qdrant_url,
            api_key=self.qdrant_api_key,
            check_compatibility=False,
        )
        self.vectorstore = QdrantVectorStore(
            client=self.client,
            collection_name=self.collection_name,
            embedding=self.embeddings,
        )
        self.reranker = None

    def initialize(self, top_candidates: int = 15, top_reranked: int = 4):
        """Initializes the Cohere reranker component."""
        cohere_key = os.getenv("COHERE_API_KEY")
        if cohere_key:
            self.reranker = CohereRerank(
                model="rerank-v3.5",
                top_n=top_reranked,
                cohere_api_key=cohere_key,
            )

    def retrieve_and_rerank(
        self, query: str, top_k: int = 4, top_candidates: int = 15
    ) -> List[dict[str, Any]]:
        if self.reranker is None:
            self.initialize(top_candidates=top_candidates, top_reranked=top_k)

        # 1. Fast vector retrieval directly from Qdrant Cloud (~30-50ms)
        docs = self.vectorstore.similarity_search(query, k=top_candidates)
        docs = self._hydrate_payloads(docs)
        docs = [doc for doc in docs if (doc.page_content or "").strip()]
        if not docs:
            return []

        # 2. Rerank top candidates with Cohere cross-encoder (~300ms)
        if self.reranker and docs:
            try:
                self.reranker.top_n = top_k
                reranked_docs = self.reranker.compress_documents(docs, query)
            except Exception as e:
                print(f"[Retrieval Warning] Cohere reranking failed: {e}. Falling back to top vector candidates.")
                reranked_docs = docs[:top_k]
        else:
            reranked_docs = docs[:top_k]

        # 3. Standardize output format for LLM synthesis (Schema remains 100% identical)
        standardized_chunks = []
        seen_segment_ids: set[str] = set()
        for doc in reranked_docs:
            excerpt = (doc.page_content or "").strip()
            if not excerpt:
                continue
            meta = doc.metadata or {}
            segment_id = _first_value(
                meta,
                "segment_id",
                "record_id",
                "chunk_id",
                "visual_record_id",
                "review_id",
                "question_id",
                "_id",
                default="seg_unknown",
            )
            if segment_id in seen_segment_ids:
                continue
            seen_segment_ids.add(segment_id)
            score = meta.get("relevance_score")
            if score is None:
                score = 0.85
            standardized_chunks.append({
                "segment_id": segment_id,
                "source_id": _first_value(
                    meta,
                    "source_id",
                    "asset_id",
                    "source_asset_id",
                    "lecture_id",
                    "record_id",
                    default="source_unknown",
                ),
                "modality": _first_value(
                    meta,
                    "modality",
                    "content_type",
                    "source_type",
                    "content_category",
                    default="text",
                ),
                "timestamp": _first_value(
                    meta,
                    "timestamp",
                    "start_time",
                    "timestamp_seconds",
                    "location",
                    default="",
                ),
                "excerpt": excerpt,
                "score": float(score),
            })
        return standardized_chunks

    def _hydrate_payloads(self, docs: list[Document]) -> list[Document]:
        point_ids = [
            doc.metadata.get("_id")
            for doc in docs
            if doc.metadata and doc.metadata.get("_id") is not None
        ]
        if not point_ids:
            return docs

        try:
            points = self.client.retrieve(
                collection_name=self.collection_name,
                ids=point_ids,
                with_payload=True,
                with_vectors=False,
            )
        except Exception as exc:
            print(f"[Retrieval Warning] Qdrant payload hydration failed: {exc}.")
            return docs

        payload_by_id = {str(point.id): point.payload or {} for point in points}
        hydrated_docs = []
        for doc in docs:
            point_id = doc.metadata.get("_id") if doc.metadata else None
            payload = payload_by_id.get(str(point_id), {})
            metadata = {**payload, **(doc.metadata or {})}
            page_content = (doc.page_content or "").strip() or _payload_text(payload)
            hydrated_docs.append(Document(page_content=page_content, metadata=metadata))
        return hydrated_docs


def _payload_text(payload: dict[str, Any]) -> str:
    fields = (
        "text",
        "searchable_text",
        "post_text",
        "visual_text",
        "summary",
        "diagram_explanation",
        "graph_explanation",
        "thread_title",
        "topic",
    )
    parts = [
        str(payload.get(field, "")).strip()
        for field in fields
        if str(payload.get(field, "")).strip()
    ]
    return "\n\n".join(parts)


def _first_value(payload: dict[str, Any], *keys: str, default: str = "") -> str:
    for key in keys:
        value = payload.get(key)
        if value is not None and str(value).strip():
            return str(value)
    return default


# Global singleton pipeline instance
pipeline = RetrievalPipeline()
