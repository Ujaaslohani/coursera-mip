# Retrieval of relevant documents from Database using Vector Search and Cohere Reranking
import os
from typing import Any, List
from dotenv import load_dotenv

from qdrant_client import QdrantClient
from langchain_qdrant import QdrantVectorStore
from langchain_huggingface import HuggingFaceEndpointEmbeddings
from langchain_cohere import CohereRerank

load_dotenv()


class RetrievalPipeline:
    def __init__(self, collection_name: str = "COURSEERA_ALMAX_MULTIMODAL"):
        self.collection_name = collection_name
        self.qdrant_url = os.getenv("QDRANT_URL")
        self.qdrant_api_key = os.getenv("QDRANT_API_KEY")

        # Serverless Cloud API (Uses ~0 MB server RAM)
        self.embeddings = HuggingFaceEndpointEmbeddings(
            model="BAAI/bge-base-en-v1.5",
            huggingfacehub_api_token=os.getenv("HF_TOKEN"),
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
        for doc in reranked_docs:
            meta = doc.metadata or {}
            score = meta.get("relevance_score")
            if score is None:
                score = 0.85
            standardized_chunks.append({
                "segment_id": meta.get("segment_id", meta.get("source_id", "seg_unknown")),
                "source_id": meta.get("source_id", meta.get("asset_id", "source_unknown")),
                "modality": meta.get("modality", "text"),
                "timestamp": meta.get("timestamp", meta.get("location", "")),
                "excerpt": doc.page_content,
                "score": float(score),
            })
        return standardized_chunks


# Global singleton pipeline instance
pipeline = RetrievalPipeline()
