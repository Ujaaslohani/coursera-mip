# LLM Synthesis using the retreived documents/chunks from the retreival pipeline
import os
import uuid
from dotenv import load_dotenv
from groq import Groq
import instructor

try:
    from schema import EvidenceSegment, InsightRecommendation, InsightSynthesis
except ImportError:
    from RAG2.schema import EvidenceSegment, InsightRecommendation, InsightSynthesis

load_dotenv()


def _get_client():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY is not set in the environment.")
    groq_client = Groq(api_key=api_key)
    return instructor.from_groq(groq_client, mode=instructor.Mode.TOOLS)

SYSTEM_PROMPT = """You are a grounded learning-analytics assistant for Coursera.

You will be given an educator's query and a list of evidence segments retrieved from course materials.

STRICT INSTRUCTIONS:
1. Base all explanations solely on the provided evidence. Do not extrapolate or fabricate facts.
2. In `friction_explanation` and `summary`, refer to lectures, slides, videos, or course concepts naturally. Do NOT output raw UUID hash strings in the prose.
3. In `cited_segment_ids`, list ONLY the exact segment_id values (e.g., UUIDs or strings) that directly support your findings.
4. If evidence is weak, incomplete, or does not mention the topic, provide low confidence (<0.5).
5. `recommended_action` must be a clear pedagogical recommendation for course creators.
"""


def _format_evidence_block(chunks: list[dict]) -> str:
    lines = []
    for c in chunks:
        loc = f" @ {c['timestamp']}" if c.get("timestamp") else ""
        lines.append(
            f"Segment ID: {c['segment_id']}\nSource: {c['source_id']} ({c['modality']}{loc})\nExcerpt: {c['excerpt']}\n"
        )
    return "\n---\n".join(lines)

# Refrencing the pydantic class to produce validated and structred output
def synthesize_insight(
    query: str, reranked_chunks: list[dict]
) -> InsightRecommendation:
    if not reranked_chunks:
        return InsightRecommendation(
            insight_id=str(uuid.uuid4()),
            query=query,
            summary="No relevant evidence was found for this query.",
            friction_explanation="Retrieval returned zero results above the confidence threshold.",
            evidence=[],
            recommended_action="Broaden the query or check whether relevant assets have been ingested.",
            confidence=0.0,
            requires_human_review=True,
        )

    evidence_block = _format_evidence_block(reranked_chunks)
    model_name = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")

    # 1. Ask LLM to generate the reasoning and pick cited IDs
    client = _get_client()
    synthesis: InsightSynthesis = client.chat.completions.create(
        model=model_name,
        response_model=InsightSynthesis,
        max_retries=2,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"User Query: {query}\n\nRetrieved Evidence:\n{evidence_block}",
            },
        ],
    )

    # 2. Build a lookup of the actual retrieval chunks
    chunk_map = {str(c["segment_id"]): c for c in reranked_chunks}

    # Filter to cited chunks; if LLM hallucinated IDs, fall back to all retrieved chunks
    selected_chunks = [
        chunk_map[sid]
        for sid in synthesis.cited_segment_ids
        if sid in chunk_map
    ]
    if not selected_chunks:
        selected_chunks = reranked_chunks

    # 3. Deterministically construct the final EvidenceSegment objects
    evidence_segments = [
        EvidenceSegment(
            segment_id=str(c["segment_id"]),
            source_id=str(c.get("source_id", "unknown")),
            modality=str(c.get("modality") or "text"),
            timestamp=str(c.get("timestamp") or ""),
            excerpt=str(c.get("excerpt") or ""),
            confidence=float(c.get("score", 0.5)),
        )
        for c in selected_chunks
    ]

    return InsightRecommendation(
        insight_id=str(uuid.uuid4()),
        query=query,
        summary=synthesis.summary,
        friction_explanation=synthesis.friction_explanation,
        evidence=evidence_segments,
        recommended_action=synthesis.recommended_action,
        confidence=synthesis.confidence,
        requires_human_review=True,
    )
