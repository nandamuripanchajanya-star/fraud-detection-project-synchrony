import numpy as np
import pandas as pd


# =========================================================
# Synthetic Digital-Lending Fraud Dataset Generator
# =========================================================

RANDOM_SEED = 42
N_ROWS = 12000

# Deliberate synthetic class balance.
# This is NOT a real-world fraud-rate claim.
FRAUD_RATE = 0.13

rng = np.random.default_rng(RANDOM_SEED)


# =========================================================
# Helper functions
# =========================================================

def clipped_normal(mean, std, minimum, maximum, size):
    """Generate normally distributed values within a range."""
    values = rng.normal(mean, std, size)
    return np.clip(values, minimum, maximum)


def clipped_lognormal(mean, sigma, minimum, maximum, size):
    """Generate log-normal values within a range."""
    values = rng.lognormal(mean, sigma, size)
    return np.clip(values, minimum, maximum)


def bernoulli_probability(probability, size):
    """Generate 0/1 values using a probability."""
    return rng.binomial(1, probability, size)

def generate_transaction_amounts(size):
    """
    Generate transaction amounts with a realistic long tail.

    Most events remain in lower/moderate ranges, while a
    smaller portion covers high-value events up to ₹5,00,000.
    """

    base = clipped_lognormal(
        mean=5.2,
        sigma=1.0,
        minimum=10,
        maximum=500000,
        size=size
    )

    # Small high-value tail
    tail_mask = rng.random(size) < 0.08

    tail_values = np.exp(
        rng.uniform(
            np.log(10000),
            np.log(500000),
            tail_mask.sum()
        )
    )

    base[tail_mask] = tail_values

    return np.clip(
        base,
        10,
        500000
    )

def generate_account_ages(size, minimum=1):
    """
    Generate account ages with a broad long-established tail.

    Most accounts remain in lower/mid ranges, while a smaller
    portion covers long-established accounts up to 50 years.
    """

    ages = np.clip(
        rng.gamma(
            shape=3.5,
            scale=180,
            size=size
        ),
        minimum,
        18250
    )

    # Small long-established-account tail
    tail_mask = rng.random(size) < 0.08

    tail_values = rng.uniform(
        3650,
        18250,
        tail_mask.sum()
    )

    ages[tail_mask] = tail_values

    return np.clip(
        ages,
        minimum,
        18250
    ).astype(int)

def generate_profile_rows(profile_name, count):
    """
    Generate rows for one behavioral profile.

    Returns a dataframe containing the eight raw features
    plus the internal profile name.
    """

    if count == 0:
        return pd.DataFrame()

    # -----------------------------------------------------
    # Legitimate profiles
    # -----------------------------------------------------

    if profile_name == "baseline_legitimate":

        transaction_amount = generate_transaction_amounts(count)

        transactions_last_10min = np.clip(
            rng.poisson(0.9, count),
            0,
            6
        )

        time_since_last_transaction = np.clip(
            rng.exponential(300, count),
            1,
            5000
        )

        device_is_new = bernoulli_probability(0.04, count)
        location_is_unusual = bernoulli_probability(0.04, count)
        ip_is_unusual = bernoulli_probability(0.03, count)
        is_unusual_time = bernoulli_probability(0.05, count)

        account_age_days = generate_account_ages(
            count,
            minimum=15
        )

    elif profile_name == "power_user":

        transaction_amount = generate_transaction_amounts(count)

        # Naturally higher activity.
        transactions_last_10min = np.clip(
            rng.poisson(1.8, count),
            0,
            6
        )

        time_since_last_transaction = np.clip(
            rng.exponential(180, count),
            1,
            4000
        )

        device_is_new = bernoulli_probability(0.05, count)
        location_is_unusual = bernoulli_probability(0.05, count)
        ip_is_unusual = bernoulli_probability(0.04, count)
        is_unusual_time = bernoulli_probability(0.06, count)

        account_age_days = generate_account_ages(
            count,
            minimum=30
        )

    elif profile_name == "device_upgrade":

        transaction_amount = generate_transaction_amounts(count)

        transactions_last_10min = np.clip(
            rng.poisson(1.0, count),
            0,
            5
        )

        time_since_last_transaction = np.clip(
            rng.exponential(280, count),
            1,
            5000
        )

        # This profile deliberately resembles account takeover.
        device_is_new = bernoulli_probability(0.85, count)
        location_is_unusual = bernoulli_probability(0.16, count)
        ip_is_unusual = bernoulli_probability(0.28, count)
        is_unusual_time = bernoulli_probability(0.07, count)

        account_age_days = generate_account_ages(
            count,
            minimum=120
        )

    elif profile_name == "new_customer":

        transaction_amount = generate_transaction_amounts(count)

        transactions_last_10min = np.clip(
            rng.poisson(0.8, count),
            0,
            5
        )

        time_since_last_transaction = np.clip(
            rng.exponential(350, count),
            1,
            5000
        )

        device_is_new = bernoulli_probability(0.25, count)
        location_is_unusual = bernoulli_probability(0.06, count)
        ip_is_unusual = bernoulli_probability(0.05, count)
        is_unusual_time = bernoulli_probability(0.06, count)

        account_age_days = np.clip(
            rng.gamma(shape=2.0, scale=7, size=count),
            1,
            45
        ).astype(int)

    elif profile_name == "returning_customer":

        transaction_amount = generate_transaction_amounts(count)
        

        # Returning users can naturally perform a small burst.
        transactions_last_10min = np.clip(
            rng.poisson(1.5, count),
            0,
            6
        )

        # Long inactivity before return.
        time_since_last_transaction = np.clip(
            rng.lognormal(
                mean=7.0,
                sigma=0.7,
                size=count
            ),
            1000,
            10000
        )

        device_is_new = bernoulli_probability(0.06, count)
        location_is_unusual = bernoulli_probability(0.07, count)
        ip_is_unusual = bernoulli_probability(0.05, count)
        is_unusual_time = bernoulli_probability(0.08, count)

        account_age_days = generate_account_ages(
            count,
            minimum=180
        )

    # -----------------------------------------------------
    # Fraud archetypes
    # -----------------------------------------------------

    elif profile_name == "high_velocity_fraud":

        transaction_amount = generate_transaction_amounts(count)

        # Stronger burst behavior, but overlaps power users.
        transactions_last_10min = np.clip(
            rng.poisson(3.0, count),
            1,
            10
        )

        time_since_last_transaction = np.clip(
            rng.exponential(12, count),
            0.2,
            1200
        )

        device_is_new = bernoulli_probability(0.30, count)
        location_is_unusual = bernoulli_probability(0.20, count)
        ip_is_unusual = bernoulli_probability(0.25, count)
        is_unusual_time = bernoulli_probability(0.18, count)

        account_age_days = generate_account_ages(
            count,
            minimum=10
        )

    elif profile_name == "account_takeover_fraud":

        transaction_amount = generate_transaction_amounts(count)

        transactions_last_10min = np.clip(
            rng.poisson(1.8, count),
            0,
            7
        )

        time_since_last_transaction = np.clip(
            rng.exponential(80, count),
            0.5,
            5000
        )

        # Strong device + network combination.
        device_is_new = bernoulli_probability(0.72, count)
        location_is_unusual = bernoulli_probability(0.46, count)
        ip_is_unusual = bernoulli_probability(0.70, count)
        is_unusual_time = bernoulli_probability(0.22, count)

        # Established accounts.
        account_age_days = generate_account_ages(
            count,
            minimum=120
        )

    elif profile_name == "new_account_fraud":

        transaction_amount = generate_transaction_amounts(count)

        # Intentionally normal-looking activity.
        transactions_last_10min = np.clip(
            rng.poisson(1.0, count),
            0,
            5
        )

        time_since_last_transaction = np.clip(
            rng.exponential(300, count),
            1,
            5000
        )

        # Fraudster may use their own known device.
        device_is_new = bernoulli_probability(0.20, count)
        location_is_unusual = bernoulli_probability(0.14, count)
        ip_is_unusual = bernoulli_probability(0.16, count)
        is_unusual_time = bernoulli_probability(0.08, count)

        account_age_days = np.clip(
            rng.gamma(shape=2.0, scale=6, size=count),
            1,
            25
        ).astype(int)

    elif profile_name == "dormant_reactivation_fraud":

        transaction_amount = generate_transaction_amounts(count)

        # Burst following dormancy.
        transactions_last_10min = np.clip(
            rng.poisson(2.5, count),
            1,
            8
        )

        time_since_last_transaction = np.clip(
            rng.lognormal(
                mean=8.0,
                sigma=0.55,
                size=count
            ),
            1000,
            10000
        )

        device_is_new = bernoulli_probability(0.30, count)
        location_is_unusual = bernoulli_probability(0.32, count)
        ip_is_unusual = bernoulli_probability(0.35, count)
        is_unusual_time = bernoulli_probability(0.30, count)

        account_age_days = generate_account_ages(
            count,
            minimum=180
        )

    else:
        raise ValueError(f"Unknown profile: {profile_name}")

    return pd.DataFrame({
        "transaction_amount": np.round(transaction_amount, 2),
        "transactions_last_10min": transactions_last_10min.astype(int),
        "time_since_last_transaction": np.round(
            time_since_last_transaction, 2
        ),
        "device_is_new": device_is_new.astype(int),
        "location_is_unusual": location_is_unusual.astype(int),
        "ip_is_unusual": ip_is_unusual.astype(int),
        "is_unusual_time": is_unusual_time.astype(int),
        "account_age_days": account_age_days.astype(int),
        "profile": profile_name
    })


# =========================================================
# 1. Define profile sizes
# =========================================================

fraud_count = round(N_ROWS * FRAUD_RATE)
legitimate_count = N_ROWS - fraud_count


# Legitimate profile distribution.
legitimate_profiles = {
    "baseline_legitimate": 0.60,
    "power_user": 0.10,
    "device_upgrade": 0.10,
    "new_customer": 0.10,
    "returning_customer": 0.10
}


# Fraud profile distribution.
fraud_profiles = {
    "high_velocity_fraud": 0.30,
    "account_takeover_fraud": 0.30,
    "new_account_fraud": 0.20,
    "dormant_reactivation_fraud": 0.20
}


# =========================================================
# 2. Allocate row counts to profiles
# =========================================================

def allocate_counts(total_count, profile_weights):
    """
    Convert profile proportions into integer row counts.
    Ensures the counts sum exactly to total_count.
    """

    names = list(profile_weights.keys())
    weights = np.array(list(profile_weights.values()), dtype=float)

    weights = weights / weights.sum()

    raw_counts = weights * total_count
    counts = np.floor(raw_counts).astype(int)

    remainder = total_count - counts.sum()

    if remainder > 0:
        fractions = raw_counts - counts

        order = np.argsort(
            fractions
        )[::-1]

        for index in order[:remainder]:
            counts[index] += 1

    return dict(zip(names, counts))


legitimate_counts = allocate_counts(
    legitimate_count,
    legitimate_profiles
)

fraud_counts = allocate_counts(
    fraud_count,
    fraud_profiles
)


# =========================================================
# 3. Generate legitimate rows
# =========================================================

frames = []

for profile_name, count in legitimate_counts.items():

    frame = generate_profile_rows(
        profile_name,
        count
    )

    frame["is_fraud"] = 0

    frames.append(frame)


# =========================================================
# 4. Generate fraud rows
# =========================================================

for profile_name, count in fraud_counts.items():

    frame = generate_profile_rows(
        profile_name,
        count
    )

    frame["is_fraud"] = 1

    frames.append(frame)


# =========================================================
# 5. Combine rows
# =========================================================

df = pd.concat(
    frames,
    ignore_index=True
)


# =========================================================
# 6. Add controlled cross-profile blending
# =========================================================
#
# A small portion of rows borrow selected behavioral
# characteristics from a confusable profile.
#
# The fraud label DOES NOT change.
#
# This intentionally creates difficult borderline examples.
# =========================================================

confusable_profiles = {
    "high_velocity_fraud": "power_user",
    "account_takeover_fraud": "device_upgrade",
    "new_account_fraud": "new_customer",
    "dormant_reactivation_fraud": "returning_customer"
}


for fraud_profile, legit_profile in confusable_profiles.items():

    candidate_indices = df.index[
        df["profile"] == fraud_profile
    ].to_numpy()

    if len(candidate_indices) == 0:
        continue

    blend_count = max(
        1,
        int(len(candidate_indices) * 0.06)
    )

    selected = rng.choice(
        candidate_indices,
        size=blend_count,
        replace=False
    )

    partner_count = max(
        1,
        int(blend_count * 1.2)
    )

    partner = generate_profile_rows(
        legit_profile,
        partner_count
    )

    for position, row_index in enumerate(selected):

        source_row = partner.iloc[
            position % len(partner)
        ]

        # Blend only selected behavioral fields.
        df.loc[row_index, "transactions_last_10min"] = (
            source_row["transactions_last_10min"]
        )

        df.loc[row_index, "time_since_last_transaction"] = (
            source_row["time_since_last_transaction"]
        )


# =========================================================
# 7. Generate derived features
# =========================================================

df["device_ip_anomaly"] = (
    df["device_is_new"]
    * df["ip_is_unusual"]
)

df["multi_signal_count"] = (
    df["device_is_new"]
    + df["location_is_unusual"]
    + df["ip_is_unusual"]
    + df["is_unusual_time"]
)


# =========================================================
# 8. Shuffle dataset
# =========================================================

df = df.sample(
    frac=1,
    random_state=RANDOM_SEED
).reset_index(drop=True)


# =========================================================
# 9. Create ML dataset
# =========================================================

ml_columns = [
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

ml_dataset = df[ml_columns]


# =========================================================
# 10. Save files
# =========================================================

ml_output = "synthetic_fraud_dataset.csv"
audit_output = "synthetic_fraud_audit.csv"

ml_dataset.to_csv(
    ml_output,
    index=False
)

# Audit file contains the hidden profile information.
# This is NOT used for ML training.
df.to_csv(
    audit_output,
    index=False
)


# =========================================================
# 11. Verification
# =========================================================

print("\n==========================================")
print("NEW ARCHETYPE-BASED DATASET GENERATED")
print("==========================================")

print(f"Rows: {len(ml_dataset)}")
print(f"ML Columns: {len(ml_dataset.columns)}")

print("\nClass Distribution:")
print(
    ml_dataset["is_fraud"]
    .value_counts()
    .sort_index()
)

fraud_rate = (
    ml_dataset["is_fraud"].mean()
    * 100
)

print(
    f"\nFraud Rate: {fraud_rate:.2f}%"
)

print("\nProfile Distribution:")
print(
    df["profile"]
    .value_counts()
)

print("\nFeature Columns:")
print(
    ml_dataset.columns.tolist()
)

print("\nFirst 10 ML Rows:")
print(
    ml_dataset.head(10)
)

print("\nFiles created:")
print(f"1. {ml_output}")
print(f"2. {audit_output}")

print("\n==========================================")
print("Generation Complete")
print("==========================================")