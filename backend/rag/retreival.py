# Retrieval of relevant documents from Database using Vector Search and Cohere Reranking
import os
from typing import Any, List
from dotenv import load_dotenv

from qdrant_client import QdrantClient
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEndpointEmbeddings
from langchain_cohere import CohereRerank

load_dotenv()


class RetrievalPipeline:
    def __init__(self, collection_name: str = "COURSEERA_ALMAX_MULTIMODAL"):
        self.collection_name = collection_name
        self.qdrant_url = os.getenv("QDRANT_URL", "https://qdrant.coursera.org")
        self.qdrant_api_key = os.getenv("QDRANT_API_KEY")

        self.embeddings = HuggingFaceEndpointEmbeddings(
            model="BAAI/bge-base-en-v1.5",
            huggingfacehub_api_token=os.getenv("HF_TOKEN"),
        )
        self.client = QdrantClient(
            url=self.qdrant_url,
            api_key=self.qdrant_api_key,
            check_compatibility=False,
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

        # 1. Direct Qdrant Search (guarantees full access to raw payload keys)
        query_vector = self.embeddings.embed_query(query)
        search_results = self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            limit=top_candidates,
            with_payload=True,
        ).points

        # 2. Convert points into LangChain Documents with complete metadata
        candidate_docs = []
        for point in search_results:
            payload = point.payload or {}

            # Extract text (captions vs quizzes)
            text_content = payload.get("text") or payload.get("question") or ""
            if payload.get("content_type") == "quiz" and payload.get("explanation"):
                text_content = f"Question: {payload.get('question')}\nExplanation: {payload.get('explanation')}"

            if text_content.strip():
                candidate_docs.append(
                    Document(page_content=text_content, metadata=payload)
                )

        # 3. Rerank with Cohere
        if self.reranker and candidate_docs:
            try:
                self.reranker.top_n = top_k
                reranked_docs = self.reranker.compress_documents(candidate_docs, query)
            except Exception as e:
                print(f"[Retrieval Warning] Cohere reranking failed: {e}. Falling back to top vector candidates.")
                reranked_docs = candidate_docs[:top_k]
        else:
            reranked_docs = candidate_docs[:top_k]

        # 4. Standardize output format
        standardized_chunks = []
        for doc in reranked_docs:
            meta = doc.metadata or {}

            # Time formatting
            timestamp = ""
            if meta.get("start_time") and meta.get("end_time"):
                timestamp = f"{meta['start_time']} - {meta['end_time']}"
            elif meta.get("start_time"):
                timestamp = str(meta["start_time"])
            elif meta.get("timestamp"):
                timestamp = str(meta["timestamp"])

            # IDs resolution
            segment_id = str(
                meta.get("chunk_id")
                or meta.get("record_id")
                or meta.get("question_id")
                or "seg_unknown"
            )
            source_id = str(
                meta.get("asset_id")
                or meta.get("source_file")
                or meta.get("lecture_id")
                or "source_unknown"
            )

            score = meta.get("relevance_score", 0.85)
            clamped_score = max(0.0, min(1.0, float(score)))

            standardized_chunks.append({
                "segment_id": segment_id,
                "source_id": source_id,
                "modality": meta.get("content_type", "text"),
                "timestamp": timestamp,
                "excerpt": doc.page_content,
                "confidence": clamped_score,
                "score": clamped_score,
            })

        return standardized_chunks


# Global singleton pipeline instances
pipeline = RetrievalPipeline()
