import re


REQUIRED_SECTIONS = [
    "Risk assessment:",
    "Why it was flagged:",
    "Relevant evidence:",
    "Recommended action:",
]


ALLOWED_DECISIONS = {
    "APPROVE",
    "REVIEW",
    "BLOCK",
}


def validate_llm_response(
    response: str,
    expected_decision: str,
) -> str:

    if not response or not response.strip():
        raise ValueError(
            "LLM returned an empty response."
        )

    cleaned = response.strip()

    # -----------------------------------------------------
    # Length guardrail
    # -----------------------------------------------------

    if len(cleaned) > 5000:
        raise ValueError(
            "LLM response exceeded the allowed length."
        )

    # -----------------------------------------------------
    # Required section guardrail
    # -----------------------------------------------------

    missing_sections = [
        section
        for section in REQUIRED_SECTIONS
        if section not in cleaned
    ]

    if missing_sections:
        raise ValueError(
            "LLM response is missing required sections: "
            + ", ".join(missing_sections)
        )

    # -----------------------------------------------------
    # Decision consistency guardrail
    # -----------------------------------------------------

    if expected_decision not in ALLOWED_DECISIONS:
        raise ValueError(
            "Invalid model decision."
        )

    # Look for an explicit decision statement rather than
    # rejecting any incidental mention of APPROVE/REVIEW/BLOCK.
    explicit_decision_patterns = [
        r"^\s*decision\s*:\s*(APPROVE|REVIEW|BLOCK)\b",
        r"^\s*recommended action\s*:\s*(APPROVE|REVIEW|BLOCK)\b",
    ]

    explicit_decisions = []

    for pattern in explicit_decision_patterns:
        matches = re.findall(
            pattern,
            cleaned,
            re.IGNORECASE | re.MULTILINE,
        )

        explicit_decisions.extend(
            match.upper()
            for match in matches
        )

    for llm_decision in explicit_decisions:
        if llm_decision != expected_decision:
            raise ValueError(
                "LLM response conflicts with "
                f"the model decision: {llm_decision}"
            )

    return cleaned