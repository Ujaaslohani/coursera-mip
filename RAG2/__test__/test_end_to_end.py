# End to End Testing of the whole Integrated RAG and LLM synthesis model wrapped in MCP
import json
import os
from dotenv import load_dotenv
from retreival import pipeline
from synthesis import synthesize_insight

load_dotenv()


def run_db_to_synthesis_test(
    test_query: str, top_candidates: int = 10, top_reranked: int = 4
):
    print("=" * 60)
    print(f"1. RUNNING RETRIEVAL ON LIVE QDRANT DB")
    print(f"Query: '{test_query}'")
    print("=" * 60)

    # 1. Fetch chunks from live Qdrant + BM25 + Cohere Rerank
    try:
        reranked_chunks = pipeline.retrieve_and_rerank(
            query=test_query, top_k=top_reranked
        )
    except Exception as e:
        print(f"\n[RETRIEVAL FAILED]: {e}")
        return

    print(f"\nRetrieved {len(reranked_chunks)} live chunks from database:")
    for idx, chunk in enumerate(reranked_chunks, 1):
        print(f"\n--- Chunk {idx} (Score: {chunk.get('score', 0):.4f}) ---")
        print(f"Source ID:  {chunk.get('source_id')}")
        print(f"Modality:   {chunk.get('modality')}")
        print(f"Location:   {chunk.get('timestamp')}")
        print(f"Excerpt:    {chunk.get('excerpt')[:120]}...")

    # 2. Feed retrieved chunks directly into Synthesis engine
    print("\n" + "=" * 60)
    print("2. PASSING DB CHUNKS TO SYNTHESIS (INSTRUCTOR / LLM)")
    print("=" * 60)

    try:
        insight = synthesize_insight(
            query=test_query, reranked_chunks=reranked_chunks
        )

        print("\n=== FINAL GENERATED INSIGHT (Live DB Grounded) ===")
        print(json.dumps(insight.model_dump(), indent=2))

    except Exception as e:
        print(f"\n[SYNTHESIS FAILED]: {e}")


if __name__ == "__main__":
    query = "Why are students struggling with Quiz Question 3 on Overfitting?"
    run_db_to_synthesis_test(query)