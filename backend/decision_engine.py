LOW_RISK_THRESHOLD = 0.40
HIGH_RISK_THRESHOLD = 0.65


def get_risk_assessment(fraud_probability: float) -> dict:
    """
    Convert fraud probability into a risk band and
    prototype response decision.
    """

    if fraud_probability < LOW_RISK_THRESHOLD:
        risk_band = "LOW"
        decision = "APPROVE"

    elif fraud_probability < HIGH_RISK_THRESHOLD:
        risk_band = "MEDIUM"
        decision = "REVIEW"

    else:
        risk_band = "HIGH"
        decision = "BLOCK"

    return {
        "risk_band": risk_band,
        "decision": decision
    }