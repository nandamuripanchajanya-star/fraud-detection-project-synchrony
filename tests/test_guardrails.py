import pytest

from backend.guardrails import validate_llm_response


VALID_RESPONSE = """
Risk assessment:
HIGH risk.

Why it was flagged:
New device and unusual IP.

Relevant evidence:
Multiple anomalies were detected.

Recommended action:
BLOCK
"""


def test_valid_llm_response():
    result = validate_llm_response(
        VALID_RESPONSE,
        "BLOCK",
    )

    assert "Risk assessment:" in result
    assert "Recommended action:" in result


def test_incidental_decision_word_is_allowed():
    response = """
Risk assessment:
HIGH risk.

Why it was flagged:
New device and unusual IP.
REVIEW may be appropriate in lower-risk cases.

Relevant evidence:
Multiple anomalies were detected.

Recommended action:
BLOCK
"""

    result = validate_llm_response(
        response,
        "BLOCK",
    )

    assert result


def test_conflicting_recommended_action_is_rejected():
    response = """
Risk assessment:
HIGH risk.

Why it was flagged:
New device and unusual IP.

Relevant evidence:
Multiple anomalies were detected.

Recommended action:
REVIEW
"""

    with pytest.raises(ValueError):
        validate_llm_response(
            response,
            "BLOCK",
        )


def test_missing_required_section_is_rejected():
    response = """
Risk assessment:
HIGH risk.

Why it was flagged:
New device and unusual IP.

Relevant evidence:
Multiple anomalies were detected.
"""

    with pytest.raises(ValueError):
        validate_llm_response(
            response,
            "BLOCK",
        )