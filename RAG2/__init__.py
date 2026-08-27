from .schema import EvidenceSegment, InsightRecommendation, InsightSynthesis
from .synthesis import synthesize_insight

# MAKE THE RAG2 IMPORTABLE PACKAGE 
__all__ = [
    "EvidenceSegment",
    "InsightRecommendation",
    "InsightSynthesis",
    "synthesize_insight",
]
