# Retreival of relevant documents from Database using hybrid search, rank fusion and Cohere Re-ranking
import os
import re
from typing import List, Tuple
from dotenv import load_dotenv

from qdrant_client import QdrantClient
from langchain_qdrant import QdrantVectorStore
from langchain_huggingface import HuggingFaceEndpointEmbeddings

from rank_bm25 import BM25Okapi
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_classic.retrievers import EnsembleRetriever, ContextualCompressionRetriever
from langchain_cohere import CohereRerank

load_dotenv()


def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


class Bm25Index:

    def __init__(self, docs: List[Document]):
        self.docs = docs
        self.bm25 = BM25Okapi([tokenize(d.page_content) for d in docs])

    def search(self, query: str, k: int = 10) -> List[Tuple[Document, float]]:
        if not self.docs:
            return []
        scores = self.bm25.get_scores(tokenize(query))
        ranked_indices = sorted(
            range(len(self.docs)), key=lambda i: -scores[i]
        )[:k]
        return [(self.docs[i], scores[i]) for i in ranked_indices]


class CustomBM25Retriever(BaseRetriever):
    bm25_index: Bm25Index
    k: int = 10

    def _get_relevant_documents(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun = None
    ) -> List[Document]:
        results = self.bm25_index.search(query, k=self.k)
        return [doc for doc, _ in results]

# Construction of the retreival pipeline for relevant chunks 
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
            url=self.qdrant_url, api_key=self.qdrant_api_key, check_compatibility=False
        )
        self.vectorstore = QdrantVectorStore(
            client=self.client,
            collection_name=self.collection_name,
            embedding=self.embeddings,
        )
        self.retriever = None

    def initialize(self, top_candidates: int = 10, top_reranked: int = 4):
        """Builds in-memory BM25 index from Qdrant and constructs the pipeline."""
        print(
            f"[Retrieval] Fetching documents from Qdrant collection '{self.collection_name}'..."
        )
        records, _ = self.client.scroll(
            collection_name=self.collection_name, limit=10000, with_payload=True
        )

        corpus_docs = []
        for r in records:
            payload = r.payload or {}
            text = payload.get(
                "page_content", payload.get("text", payload.get("excerpt", ""))
            )
            # Retain ID and metadata
            metadata = {
                k: v
                for k, v in payload.items()
                if k not in ["page_content", "text"]
            }
            metadata["segment_id"] = str(r.id)
            corpus_docs.append(Document(page_content=text, metadata=metadata))

        print(
            f"[Retrieval] Indexed {len(corpus_docs)} documents into BM25 engine."
        )

        # Vector Retriever
        vector_retriever = self.vectorstore.as_retriever(
            search_kwargs={"k": top_candidates}
        )

        # BM25 Retriever
        bm25_index = Bm25Index(corpus_docs)
        sparse_retriever = CustomBM25Retriever(
            bm25_index=bm25_index, k=top_candidates
        )

        # Hybrid RRF Fusion
        ensemble_retriever = EnsembleRetriever(
            retrievers=[sparse_retriever, vector_retriever], weights=[0.5, 0.5]
        )

        # Cohere Reranker
        compressor = CohereRerank(
            model="rerank-v3.5",
            top_n=top_reranked,
            cohere_api_key=os.getenv("COHERE_API_KEY"),
        )

        self.retriever = ContextualCompressionRetriever(
            base_compressor=compressor, base_retriever=ensemble_retriever
        )

    def retrieve_and_rerank(
        self, query: str, top_k: int = 4
    ) -> List[dict]:
        if self.retriever is None:
            self.initialize(top_reranked=top_k)

        reranked_docs = self.retriever.invoke(query)

        # Standardize output for synthesis
        standardized_chunks = []
        for doc in reranked_docs:
            meta = doc.metadata
            standardized_chunks.append({
                "segment_id": meta.get("segment_id", meta.get("source_id", "seg_unknown")),
                "source_id": meta.get("source_id", meta.get("asset_id", "source_unknown")),
                "modality": meta.get("modality", "text"),
                "timestamp": meta.get("timestamp", meta.get("location", "")),
                "excerpt": doc.page_content,
                "score": float(meta.get("relevance_score", 0.85)),
            })
        return standardized_chunks


# Global singleton pipeline instance
pipeline = RetrievalPipeline()
