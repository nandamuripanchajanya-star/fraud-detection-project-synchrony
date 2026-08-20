from schemas import FraudEvent


def generate_explanation(event: FraudEvent) -> list[str]:
    """
    Generate transparent explanations from the observed
    behavioral signals.

    These are deterministic explanations based on the
    input event. No LLM is used here.
    """

    reasons = []

    # High recent activity
    if event.transactions_last_10min >= 4:
        reasons.append(
            "High recent activity detected"
        )

    # Very short gap between events
    if event.time_since_last_transaction < 10:
        reasons.append(
            "Very short time since the previous event"
        )

    # New device
    if event.device_is_new == 1:
        reasons.append(
            "Event originated from a new device"
        )

    # Unusual location
    if event.location_is_unusual == 1:
        reasons.append(
            "Unusual location detected"
        )

    # Unusual network/IP
    if event.ip_is_unusual == 1:
        reasons.append(
            "Unusual network/IP context detected"
        )

    # Unusual time
    if event.is_unusual_time == 1:
        reasons.append(
            "Event occurred at an unusual time"
        )

    # New account
    if event.account_age_days < 30:
        reasons.append(
            "Account is relatively new"
        )

    # Large amount
    if event.transaction_amount >= 3000:
        reasons.append(
            "Transaction amount is relatively high"
        )

    # If nothing unusual was found
    if not reasons:
        reasons.append(
            "No major behavioral anomalies detected"
        )

    return reasons