import os
import joblib
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score
)
from sklearn.model_selection import train_test_split


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

DATA_FILE = "synthetic_fraud_dataset.csv"
MODEL_FILE = "fraud_model.joblib"

RANDOM_SEED = 42


# ---------------------------------------------------------
# 1. Load dataset
# ---------------------------------------------------------

print("\n==========================================")
print("Fraud Detection Model Training")
print("==========================================")

if not os.path.exists(DATA_FILE):
    raise FileNotFoundError(
        f"Dataset not found: {DATA_FILE}"
    )

df = pd.read_csv(DATA_FILE)

print(f"\nDataset loaded: {df.shape[0]} rows, {df.shape[1]} columns")


# ---------------------------------------------------------
# 2. Define features and target
# ---------------------------------------------------------

feature_columns = [
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

target_column = "is_fraud"

X = df[feature_columns]
y = df[target_column]


# ---------------------------------------------------------
# 3. Split into training and testing sets
# ---------------------------------------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    stratify=y,
    random_state=RANDOM_SEED
)

print("\nData split:")
print(f"Training samples: {len(X_train)}")
print(f"Testing samples : {len(X_test)}")

print(
    f"Training fraud rate: {y_train.mean() * 100:.2f}%"
)

print(
    f"Testing fraud rate : {y_test.mean() * 100:.2f}%"
)


# ---------------------------------------------------------
# 4. Create baseline Random Forest model
# ---------------------------------------------------------

model = RandomForestClassifier(
    n_estimators=200,
    max_depth=8,
    random_state=RANDOM_SEED,
    class_weight="balanced",
    n_jobs=-1
)


# ---------------------------------------------------------
# 5. Train model
# ---------------------------------------------------------

print("\nTraining model...")

model.fit(X_train, y_train)

print("Training complete.")


# ---------------------------------------------------------
# 6. Generate predictions
# ---------------------------------------------------------

y_pred = model.predict(X_test)
y_probability = model.predict_proba(X_test)[:, 1]


# ---------------------------------------------------------
# 7. Calculate evaluation metrics
# ---------------------------------------------------------

accuracy = accuracy_score(y_test, y_pred)

precision = precision_score(
    y_test,
    y_pred,
    zero_division=0
)

recall = recall_score(
    y_test,
    y_pred,
    zero_division=0
)

f1 = f1_score(
    y_test,
    y_pred,
    zero_division=0
)

roc_auc = roc_auc_score(
    y_test,
    y_probability
)


# ---------------------------------------------------------
# 8. Print results
# ---------------------------------------------------------

print("\n==========================================")
print("MODEL PERFORMANCE")
print("==========================================")

print(f"Accuracy : {accuracy:.4f}")
print(f"Precision: {precision:.4f}")
print(f"Recall   : {recall:.4f}")
print(f"F1 Score : {f1:.4f}")
print(f"ROC-AUC  : {roc_auc:.4f}")


print("\nClassification Report:")
print(
    classification_report(
        y_test,
        y_pred,
        target_names=["Legitimate", "Fraud"],
        zero_division=0
    )
)


print("Confusion Matrix:")
print(confusion_matrix(y_test, y_pred))


# ---------------------------------------------------------
# 9. Feature importance
# ---------------------------------------------------------

feature_importance = pd.DataFrame({
    "feature": feature_columns,
    "importance": model.feature_importances_
})

feature_importance = feature_importance.sort_values(
    by="importance",
    ascending=False
)

print("\nFeature Importance:")
print(feature_importance.to_string(index=False))


# ---------------------------------------------------------
# 10. Save trained model
# ---------------------------------------------------------

joblib.dump(model, MODEL_FILE)

print("\n==========================================")
print(f"Model saved as: {MODEL_FILE}")
print("==========================================")