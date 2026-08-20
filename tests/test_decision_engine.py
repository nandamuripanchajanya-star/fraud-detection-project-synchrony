from backend.decision_engine import get_risk_assessment


def test_low_risk_decision():
    result = get_risk_assessment(0.20)

    assert result["risk_band"] == "LOW"
    assert result["decision"] == "APPROVE"


def test_medium_risk_decision():
    result = get_risk_assessment(0.60)

    assert result["risk_band"] == "MEDIUM"
    assert result["decision"] == "REVIEW"


def test_high_risk_decision():
    result = get_risk_assessment(0.90)

    assert result["risk_band"] == "HIGH"
    assert result["decision"] == "BLOCK"