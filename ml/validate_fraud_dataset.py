import pandas as pd


DATA_FILE = "synthetic_fraud_dataset.csv"
AUDIT_FILE = "synthetic_fraud_audit.csv"


# =========================================================
# 1. Load files
# =========================================================

df = pd.read_csv(DATA_FILE)
audit = pd.read_csv(AUDIT_FILE)


print("\n==========================================")
print("ARCHETYPE DATASET VALIDATION")
print("==========================================")


# =========================================================
# 2. Basic structure
# =========================================================

print("\n[1] Dataset Shape")
print(f"Rows    : {df.shape[0]}")
print(f"Columns : {df.shape[1]}")

print("\nML Columns:")
print(df.columns.tolist())


# =========================================================
# 3. Expected columns
# =========================================================

expected_columns = [
    "transaction_amount",
    "transactions_last_10min",
    "time_since_last_transaction",
    "device_is_new",
    "location_is_unusual",
    "ip_is_unusual",
    "is_unusual_time",
    "account_age_days",
    "device_ip_anomaly",
    "multi_signal_count",
    "is_fraud"
]

print("\n[2] Column Validation")

if df.columns.tolist() == expected_columns:
    print("PASS: Columns are exactly as expected")
else:
    print("WARNING: Column structure differs")


# =========================================================
# 4. Missing values
# =========================================================

print("\n[3] Missing Values")

missing = df.isnull().sum()

print(missing)

if missing.sum() == 0:
    print("PASS: No missing values")
else:
    print("WARNING: Missing values found")


# =========================================================
# 5. Duplicate rows
# =========================================================

print("\n[4] Duplicate Rows")

duplicates = df.duplicated().sum()

print(f"Duplicate rows: {duplicates}")

if duplicates == 0:
    print("PASS")
else:
    print("WARNING")


# =========================================================
# 6. Binary features
# =========================================================

binary_columns = [
    "device_is_new",
    "location_is_unusual",
    "ip_is_unusual",
    "is_unusual_time",
    "device_ip_anomaly",
    "is_fraud"
]

print("\n[5] Binary Feature Validation")

for column in binary_columns:

    values = sorted(df[column].unique())

    print(f"{column}: {values}")

    if set(values).issubset({0, 1}):
        print("  PASS")
    else:
        print("  WARNING")


# =========================================================
# 7. Numeric ranges
# =========================================================

print("\n[6] Numeric Range Validation")

range_checks = {
    "transaction_amount": (10, 500000),
    "transactions_last_10min": (0, 10),
    "time_since_last_transaction": (0.1, 10000),
    "account_age_days": (1, 18250),
    "multi_signal_count": (0, 4)
}

for column, (minimum, maximum) in range_checks.items():

    actual_min = df[column].min()
    actual_max = df[column].max()

    print(
        f"{column}: "
        f"min={actual_min}, "
        f"max={actual_max}"
    )

    if actual_min >= minimum and actual_max <= maximum:
        print("  PASS")
    else:
        print("  WARNING")


# =========================================================
# 8. Fraud class distribution
# =========================================================

print("\n[7] Class Distribution")

print(
    df["is_fraud"]
    .value_counts()
    .sort_index()
)

fraud_rate = df["is_fraud"].mean() * 100

print(f"\nFraud rate: {fraud_rate:.2f}%")

if 12 <= fraud_rate <= 15:
    print("PASS: Within our intended synthetic range")
else:
    print("WARNING")


# =========================================================
# 9. Binary signal rates
# =========================================================

print("\n[8] Behavioral Signal Rates")

for column in [
    "device_is_new",
    "location_is_unusual",
    "ip_is_unusual",
    "is_unusual_time"
]:

    rate = df[column].mean() * 100

    print(f"{column}: {rate:.2f}% = 1")


# =========================================================
# 10. Compare legitimate vs fraud
# =========================================================

print("\n[9] Feature Means by Class")

model_features = [
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

print(
    df.groupby("is_fraud")[model_features].mean()
)


# =========================================================
# 11. Correlation inspection
# =========================================================

print("\n[10] Correlation With is_fraud")

correlations = (
    df[model_features + ["is_fraud"]]
    .corr()["is_fraud"]
    .drop("is_fraud")
    .sort_values(ascending=False)
)

print(correlations)


# =========================================================
# 12. Hidden profile distribution
# =========================================================

print("\n[11] Archetype Distribution")

print(
    audit["profile"]
    .value_counts()
)


# =========================================================
# 13. Fraud archetype averages
# =========================================================

print("\n[12] Fraud Archetype Behaviour")

fraud_profiles = audit[
    audit["is_fraud"] == 1
]

print(
    fraud_profiles
    .groupby("profile")[model_features]
    .mean()
)


# =========================================================
# 14. Legitimate profile averages
# =========================================================

print("\n[13] Legitimate Profile Behaviour")

legit_profiles = audit[
    audit["is_fraud"] == 0
]

print(
    legit_profiles
    .groupby("profile")[model_features]
    .mean()
)


# =========================================================
# 15. Sample rows
# =========================================================

print("\n[14] Sample ML Rows")

print(
    df.head(10).to_string(index=False)
)


# =========================================================
# 16. Final result
# =========================================================

print("\n==========================================")
print("VALIDATION COMPLETE")
print("==========================================")