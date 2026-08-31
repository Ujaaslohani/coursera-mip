# Defining a pydantic schema for validation and structured output response from LLM synthesis 
from typing import List, Literal
from pydantic import BaseModel, Field

Modality = str


class EvidenceSegment(BaseModel):
    segment_id: str = Field(
        ..., description="Unique ID of the retrieved chunk"
    )
    source_id: str = Field(
        ..., description="ID of the parent asset (video, doc, etc.)"
    )
    modality: str = Field(
        default="text",
        description="Type of evidence: caption, slide, frame, transcript, quiz, discussion, video, etc.",
    )
    timestamp: str = Field(
        default="",
        description="Timestamp/location within the source, empty string if not applicable",
    )
    excerpt: str = Field(
        ..., description="The actual text/description of this evidence chunk"
    )
    confidence: float = Field(
        ge=0,
        le=1,
        description="Retrieval/relevance confidence for this segment",
    )


class InsightSynthesis(BaseModel):
    """Schema strictly for LLM tool generation."""

    summary: str = Field(
        ..., description="A concise 1 to 2 sentence headline/TL;DR stating the core issue (e.g., 'Students mistake fast training loss convergence for good generalization.')."
    )
    friction_explanation: str = Field(
        ..., description="Detailed, step-by-step diagnostic breakdown explaining the conceptual misconception, citing specific lectures/slides/quizzes without repeating the summary."
    )
    cited_segment_ids: List[str] = Field(
        ...,
        description="List of segment_id strings from the evidence directly supporting this conclusion",
    )
    recommended_action: str = Field(
        ..., description="Concrete, reviewable suggestion for educators"
    )
    confidence: float = Field(
        ge=0,
        le=1,
        description="Confidence score (0.0 to 1.0) based on evidence clarity",
    )


class InsightRecommendation(BaseModel):
    """Final unified output model."""

    insight_id: str
    query: str
    summary: str
    friction_explanation: str
    evidence: List[EvidenceSegment]
    recommended_action: str
    confidence: float
    requires_human_review: bool = True