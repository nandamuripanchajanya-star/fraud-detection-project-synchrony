import joblib
import pandas as pd

from sklearn.metrics import (
    precision_score,
    recall_score,
    f1_score
)
from sklearn.model_selection import train_test_split


DATA_FILE = "synthetic_fraud_dataset.csv"
MODEL_FILE = "fraud_model.joblib"

RANDOM_SEED = 42

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
# 1. Load dataset and model
# ---------------------------------------------------------

df = pd.read_csv(DATA_FILE)

model = joblib.load(MODEL_FILE)


# ---------------------------------------------------------
# 2. Recreate the same test set
# ---------------------------------------------------------

X = df[FEATURE_COLUMNS]
y = df["is_fraud"]

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    stratify=y,
    random_state=RANDOM_SEED
)


# ---------------------------------------------------------
# 3. Get fraud probabilities
# ---------------------------------------------------------

probabilities = model.predict_proba(X_test)[:, 1]


# ---------------------------------------------------------
# 4. Evaluate thresholds
# ---------------------------------------------------------

thresholds = [
    0.40,
    0.45,
    0.50,
    0.55,
    0.60,
    0.65,
    0.70,
    0.75,
    0.80
]

print("\n==========================================")
print("THRESHOLD EVALUATION")
print("==========================================")

print(
    "\nThreshold | Precision | Recall | F1 Score"
)

print("------------------------------------------")

for threshold in thresholds:

    predictions = (
        probabilities >= threshold
    ).astype(int)

    precision = precision_score(
        y_test,
        predictions,
        zero_division=0
    )

    recall = recall_score(
        y_test,
        predictions,
        zero_division=0
    )

    f1 = f1_score(
        y_test,
        predictions,
        zero_division=0
    )

    print(
        f"{threshold:9.2f} | "
        f"{precision:9.4f} | "
        f"{recall:6.4f} | "
        f"{f1:8.4f}"
    )


print("\n==========================================")
print("Analysis complete")
print("==========================================")