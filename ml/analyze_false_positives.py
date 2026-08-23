import joblib
import pandas as pd

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
# 1. Load data and model
# ---------------------------------------------------------

df = pd.read_csv(DATA_FILE)
model = joblib.load(MODEL_FILE)


# ---------------------------------------------------------
# 2. Recreate the same test split
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
# 3. Generate predictions and probabilities
# ---------------------------------------------------------

probabilities = model.predict_proba(X_test)[:, 1]
predictions = (probabilities >= 0.5).astype(int)


results = X_test.copy()

results["actual_fraud"] = y_test.values
results["fraud_probability"] = probabilities
results["predicted_fraud"] = predictions


# ---------------------------------------------------------
# 4. False positives
# ---------------------------------------------------------

false_positives = results[
    (results["actual_fraud"] == 0) &
    (results["predicted_fraud"] == 1)
].copy()


print("\n==========================================")
print("FALSE POSITIVE ANALYSIS")
print("==========================================")

print(f"\nFalse positives: {len(false_positives)}")

print("\nAverage fraud probability of false positives:")
print(
    f"{false_positives['fraud_probability'].mean():.4f}"
)


print("\nFalse-positive feature averages:")
print(
    false_positives[FEATURE_COLUMNS].mean()
)


# ---------------------------------------------------------
# 5. Compare legitimate events overall vs false positives
# ---------------------------------------------------------

legitimate = results[
    results["actual_fraud"] == 0
]

comparison = pd.DataFrame({
    "All_Legitimate": legitimate[FEATURE_COLUMNS].mean(),
    "False_Positives": false_positives[FEATURE_COLUMNS].mean()
})

print("\n==========================================")
print("LEGITIMATE VS FALSE POSITIVE")
print("==========================================")

print(comparison)


# ---------------------------------------------------------
# 6. Probability distribution of false positives
# ---------------------------------------------------------

print("\n==========================================")
print("FALSE POSITIVE PROBABILITY DISTRIBUTION")
print("==========================================")

bins = [0.5, 0.6, 0.7, 0.8, 0.9, 1.0]

probability_groups = pd.cut(
    false_positives["fraud_probability"],
    bins=bins,
    include_lowest=True
)

print(
    probability_groups
    .value_counts()
    .sort_index()
)


# ---------------------------------------------------------
# 7. Highest-confidence false positives
# ---------------------------------------------------------

print("\n==========================================")
print("TOP 15 HIGHEST-CONFIDENCE FALSE POSITIVES")
print("==========================================")

columns_to_show = FEATURE_COLUMNS + [
    "fraud_probability"
]

print(
    false_positives
    .sort_values("fraud_probability", ascending=False)
    [columns_to_show]
    .head(15)
    .to_string(index=False)
)


# ---------------------------------------------------------
# 8. False-positive rate at different thresholds
# ---------------------------------------------------------

print("\n==========================================")
print("THRESHOLD ANALYSIS")
print("==========================================")

for threshold in [0.30, 0.40, 0.50, 0.60, 0.70, 0.80]:

    predicted = (
        probabilities >= threshold
    ).astype(int)

    fp = (
        (y_test.values == 0) &
        (predicted == 1)
    ).sum()

    tp = (
        (y_test.values == 1) &
        (predicted == 1)
    ).sum()

    fn = (
        (y_test.values == 1) &
        (predicted == 0)
    ).sum()

    print(
        f"Threshold {threshold:.2f} | "
        f"FP={fp:4d} | "
        f"TP={tp:4d} | "
        f"FN={fn:4d}"
    )


print("\n==========================================")
print("Analysis complete")
print("==========================================")