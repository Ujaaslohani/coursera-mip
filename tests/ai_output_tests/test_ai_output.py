import pytest
from pydantic import ValidationError

from backend.rag.schema import InsightSynthesis


def test_confidence_must_be_between_zero_and_one():
    valid_output = InsightSynthesis(
        summary="Students are struggling with overfitting.",
        friction_explanation="The model performs well on training data but poorly on unseen data.",
        cited_segment_ids=["seg_001"],
        recommended_action="Review the difference between training and test performance.",
        confidence=0.9,
    )

    assert 0 <= valid_output.confidence <= 1


def test_confidence_above_one_is_rejected():
    with pytest.raises(ValidationError):
        InsightSynthesis(
            summary="Students are struggling with overfitting.",
            friction_explanation="The model performs well on training data but poorly on unseen data.",
            cited_segment_ids=["seg_001"],
            recommended_action="Review training and test performance.",
            confidence=1.5,
        )