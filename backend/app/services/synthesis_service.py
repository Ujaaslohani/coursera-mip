from statistics import mean
from typing import Any

from app.models import (
    Citation,
    ContextResponse,
    EvidenceContext,
    EvidenceSaveItem,
    RecommendationSaveItem,
    SynthesizeRequest,
)


def build_answer(request: SynthesizeRequest, context: ContextResponse) -> str:
    if request.generated_answer:
        return request.generated_answer

    if not context.context:
        return (
            "No relevant evidence was retrieved for this query, so the backend "
            "cannot produce a grounded recommendation yet."
        )

    evidence_lines = []
    snippets = []
    for index, item in enumerate(context.context[:5], start=1):
        source = item.asset_id or item.source_id or item.point_id
        location = f", {item.timestamp}" if item.timestamp else ""
        text = _preview(item.text, 280)
        snippets.append(text)
        evidence_lines.append(f"{index}. {source}{location}: {text}")

    diagnostic = _diagnostic_summary(request.query, snippets)

    return (
        f"Summary: {diagnostic}\n\n"
        "Evidence used:\n\n"
        + "\n".join(evidence_lines)
        + "\n\nRecommended action: review these cited moments and add a "
        "short bridge explanation that connects the core concept, the training "
        "procedure, and why the retrieved examples matter for learners."
    )


def build_citations(context: ContextResponse) -> list[Citation]:
    return [
        Citation(
            point_id=item.point_id,
            content_type=item.content_type,
            lecture_id=item.lecture_id,
            score=item.score,
            text_preview=_preview(item.text, 180),
        )
        for item in context.context
    ]


def estimate_confidence(context: ContextResponse) -> float:
    scores = [item.score for item in context.context if item.score is not None]
    if not scores:
        return 0.35 if context.context else 0.0
    return round(max(0.0, min(1.0, mean(scores))), 3)


def evidence_for_supabase(context: ContextResponse) -> list[EvidenceSaveItem]:
    evidence = []
    for rank, item in enumerate(context.context, start=1):
        payload = item.payload or {}
        evidence.append(
            EvidenceSaveItem(
                point_id=item.point_id,
                content_type=item.content_type or payload.get("content_type") or "caption",
                lecture_id=item.lecture_id or payload.get("lecture_id"),
                module_id=_as_str(payload.get("module_id")),
                score=item.score,
                retrieval_rank=rank,
                text=item.text,
                asset_path=_as_str(payload.get("asset_path")),
                timestamp_seconds=_timestamp_seconds(payload),
                metadata={
                    "asset_id": item.asset_id,
                    "course_id": item.course_id,
                    "source_id": item.source_id,
                },
            )
        )
    return evidence


def recommendations_for_supabase(
    request: SynthesizeRequest, context: ContextResponse
) -> list[RecommendationSaveItem]:
    if request.recommendations:
        return request.recommendations

    target = context.context[0].point_id if context.context else None
    return [
        RecommendationSaveItem(
            recommendation_type="content_review",
            recommendation_text=(
                "Review the retrieved evidence and decide whether the lesson "
                "needs clearer explanation, stronger visual support, or adjusted assessment wording."
            ),
            target_record_id=target,
            priority=1,
            metadata={"generated_by": "backend-extractive-synthesis"},
        )
    ]


def context_from_evidence(query: str, evidence: list[EvidenceContext]) -> ContextResponse:
    return ContextResponse(query=query, evidence_count=len(evidence), context=evidence)


def _preview(value: str, limit: int) -> str:
    text = " ".join((value or "").split())
    if len(text) <= limit:
        return text
    return text[: limit - 3].rstrip() + "..."


def _diagnostic_summary(query: str, snippets: list[str]) -> str:
    joined = " ".join(snippets).lower()

    if "adversarial" in query.lower() or "adversarial" in joined:
        reasons = []
        if "perturb" in joined or "gradient" in joined:
            reasons.append(
                "the concept depends on perturbations and gradient-based updates, "
                "which can feel like a second optimization problem inside training"
            )
        if "computationally expensive" in joined or "inner training loop" in joined:
            reasons.append(
                "the retrieved evidence says the method can introduce an inner "
                "training loop for each data point"
            )
        if "robust" in joined or "non-robust" in joined:
            reasons.append(
                "learners must distinguish robust and non-robust features, which "
                "is an abstract shift from ordinary classification"
            )
        if reasons:
            return "Learners may be confused about adversarial training because " + "; ".join(reasons) + "."

    if "regularization" in query.lower() or "overfitting" in query.lower():
        return (
            "Learners may be confused because the retrieved evidence connects model "
            "behavior, training choices, and generalization; those ideas often need "
            "an explicit bridge between the symptom and the corrective technique."
        )

    return (
        "The retrieved evidence identifies relevant course moments, but the backend "
        "fallback synthesis should be treated as a review draft rather than a final "
        "educator-approved explanation."
    )


def _timestamp_seconds(payload: dict[str, Any]) -> float | None:
    value = payload.get("timestamp_seconds")
    if value is None:
        value = payload.get("start_seconds")
    try:
        return float(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def _as_str(value: Any) -> str | None:
    if value is None:
        return None
    return str(value)
