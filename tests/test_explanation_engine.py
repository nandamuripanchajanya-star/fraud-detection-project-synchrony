from schemas import FraudEvent
from explanation_engine import generate_explanation


def test_new_device_reason():
    event = FraudEvent(
        transaction_amount=50000,
        transactions_last_10min=1,
        time_since_last_transaction=60,
        device_is_new=1,
        location_is_unusual=0,
        ip_is_unusual=0,
        is_unusual_time=0,
        account_age_days=365,
    )

    reasons = generate_explanation(event)

    assert any(
        "device" in reason.lower()
        for reason in reasons
    )


def test_high_velocity_reason():
    event = FraudEvent(
        transaction_amount=50000,
        transactions_last_10min=5,
        time_since_last_transaction=2,
        device_is_new=0,
        location_is_unusual=0,
        ip_is_unusual=0,
        is_unusual_time=0,
        account_age_days=365,
    )

    reasons = generate_explanation(event)

    assert any(
        "high recent activity" in reason.lower()
        for reason in reasons
    )

    assert any(
        "short time" in reason.lower()
        for reason in reasons
    )


def test_multiple_risk_signals_generate_multiple_reasons():
    event = FraudEvent(
        transaction_amount=50000,
        transactions_last_10min=5,
        time_since_last_transaction=2,
        device_is_new=1,
        location_is_unusual=1,
        ip_is_unusual=1,
        is_unusual_time=1,
        account_age_days=20,
    )

    reasons = generate_explanation(event)

    assert len(reasons) >= 3