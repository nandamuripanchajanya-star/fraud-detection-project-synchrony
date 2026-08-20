from pathlib import Path

import joblib
import pandas as pd

from schemas import FraudEvent


# ---------------------------------------------------------
# Model location
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

MODEL_PATH = (
    PROJECT_ROOT
    / "ml"
    / "fraud_model.joblib"
)


# ---------------------------------------------------------
# Load the trained model once when the backend starts
# ---------------------------------------------------------

if not MODEL_PATH.exists():
    raise FileNotFoundError(
        f"Trained fraud model not found at: {MODEL_PATH}"
    )

model = joblib.load(MODEL_PATH)


# ---------------------------------------------------------
# Model feature order
# ---------------------------------------------------------

FEATURE_COLUMNS = [
    "transaction_amount",
    "transactions_last_10min",
    "time_since_last_transaction",
    "device_is_new",
    "location_is_unusual",
    "ip_is_unusual",
    "is_unusual_time",
    "account_age_days",
    "device_ip_anomaly",
    "multi_signal_count"
]


# ---------------------------------------------------------
# Predict fraud probability
# ---------------------------------------------------------

def predict_fraud(event: FraudEvent) -> float:
    """
    Calculate derived behavioral features and return
    the model's fraud probability.
    """

    # Derived feature 1:
    # New device + unusual IP/network
    device_ip_anomaly = (
        event.device_is_new
        * event.ip_is_unusual
    )

    # Derived feature 2:
    # Count of unusual behavioral signals
    multi_signal_count = (
        event.device_is_new
        + event.location_is_unusual
        + event.ip_is_unusual
        + event.is_unusual_time
    )

    # Create one-row dataframe in the exact feature order
    model_input = pd.DataFrame([{
        "transaction_amount": event.transaction_amount,
        "transactions_last_10min": event.transactions_last_10min,
        "time_since_last_transaction": event.time_since_last_transaction,
        "device_is_new": event.device_is_new,
        "location_is_unusual": event.location_is_unusual,
        "ip_is_unusual": event.ip_is_unusual,
        "is_unusual_time": event.is_unusual_time,
        "account_age_days": event.account_age_days,
        "device_ip_anomaly": device_ip_anomaly,
        "multi_signal_count": multi_signal_count
    }])

    model_input = model_input[FEATURE_COLUMNS]

    # Get probability of class 1 = fraud
    fraud_probability = model.predict_proba(
        model_input
    )[0][1]

    return float(fraud_probability)