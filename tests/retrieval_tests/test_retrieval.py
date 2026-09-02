from langchain_core.documents import Document
from rank_bm25 import BM25Okapi
import re


def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


class TestBm25Index:
    def test_returns_relevant_document_first(self):
        documents = [
            Document(page_content="Python programming basics"),
            Document(
                page_content="Overfitting happens when a model memorizes the training data."
            ),
            Document(page_content="Database indexing improves query performance"),
        ]

        bm25 = BM25Okapi(
            [tokenize(doc.page_content) for doc in documents]
        )

        scores = bm25.get_scores(tokenize("overfitting"))

        ranked_indices = sorted(
            range(len(documents)),
            key=lambda i: -scores[i]
        )

        results = [documents[i] for i in ranked_indices]

        assert len(results) == 3
        assert "overfitting" in results[0].page_content.lower()