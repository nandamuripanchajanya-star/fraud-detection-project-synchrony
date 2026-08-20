import joblib
import pandas as pd

from sklearn.inspection import permutation_importance
from sklearn.metrics import (
    average_precision_score,
    brier_score_loss,
    classification_report,
    confusion_matrix,
    roc_auc_score
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
# Load data and model
# ---------------------------------------------------------

df = pd.read_csv(DATA_FILE)
model = joblib.load(MODEL_FILE)

X = df[FEATURE_COLUMNS]
y = df["is_fraud"]


# ---------------------------------------------------------
# Recreate the same test set
# ---------------------------------------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    stratify=y,
    random_state=RANDOM_SEED
)


# ---------------------------------------------------------
# Predictions
# ---------------------------------------------------------

probabilities = model.predict_proba(X_test)[:, 1]

predictions = (
    probabilities >= 0.65
).astype(int)


# ---------------------------------------------------------
# Main evaluation metrics
# ---------------------------------------------------------

roc_auc = roc_auc_score(
    y_test,
    probabilities
)

pr_auc = average_precision_score(
    y_test,
    probabilities
)

brier = brier_score_loss(
    y_test,
    probabilities
)


print("\n==========================================")
print("FINAL MODEL EVALUATION")
print("==========================================")

print(f"\nROC-AUC : {roc_auc:.4f}")
print(f"PR-AUC  : {pr_auc:.4f}")
print(f"Brier   : {brier:.4f}")


# ---------------------------------------------------------
# Operating point at 0.65
# ---------------------------------------------------------

print("\n==========================================")
print("OPERATING POINT: THRESHOLD 0.65")
print("==========================================")

print(
    classification_report(
        y_test,
        predictions,
        target_names=["Legitimate", "Fraud"],
        zero_division=0
    )
)

print("Confusion Matrix:")
print(
    confusion_matrix(
        y_test,
        predictions
    )
)


# ---------------------------------------------------------
# Permutation importance
# ---------------------------------------------------------

print("\n==========================================")
print("PERMUTATION IMPORTANCE")
print("==========================================")

permutation = permutation_importance(
    model,
    X_test,
    y_test,
    n_repeats=10,
    random_state=RANDOM_SEED,
    scoring="average_precision"
)

importance = pd.DataFrame({
    "feature": FEATURE_COLUMNS,
    "importance_mean": permutation.importances_mean,
    "importance_std": permutation.importances_std
})

importance = importance.sort_values(
    by="importance_mean",
    ascending=False
)

print(
    importance.to_string(index=False)
)


# ---------------------------------------------------------
# Probability bands
# ---------------------------------------------------------

print("\n==========================================")
print("PROBABILITY BAND DISTRIBUTION")
print("==========================================")

bands = pd.cut(
    probabilities,
    bins=[0.0, 0.40, 0.65, 1.0],
    labels=["LOW", "MEDIUM", "HIGH"],
    include_lowest=True
)

band_summary = pd.DataFrame({
    "band": bands,
    "actual_fraud": y_test.values
}).groupby(
    "band",
    observed=True
).agg(
    events=("actual_fraud", "count"),
    fraud_count=("actual_fraud", "sum"),
    observed_fraud_rate=("actual_fraud", "mean")
)

print(band_summary)


print("\n==========================================")
print("Evaluation complete")
print("==========================================")