import random


def generate_simulated_event():
    """
    Generate one coherent synthetic digital-lending event.

    The event is based on an internal behavioral archetype.
    This is a prototype simulation of an upstream transaction
    system, not a connection to a real production system.
    """

    archetype = random.choice([
        "baseline_legitimate",
        "power_user",
        "new_customer",
        "returning_customer",
        "device_upgrade",
        "high_velocity_fraud",
        "account_takeover_fraud",
        "new_account_fraud",
        "dormant_reactivation_fraud",
    ])

    # -----------------------------------------------------
    # Legitimate baseline
    # -----------------------------------------------------

    if archetype == "baseline_legitimate":
        transaction_amount = round(
            random.uniform(100, 5000), 2
        )
        transactions_last_10min = random.randint(0, 2)
        time_since_last_transaction = round(
            random.uniform(60, 720), 2
        )
        device_is_new = 0
        location_is_unusual = 0
        ip_is_unusual = 0
        is_unusual_time = 0
        account_age_days = random.randint(
            180, 3650
        )

    # -----------------------------------------------------
    # Power user
    # -----------------------------------------------------

    elif archetype == "power_user":
        transaction_amount = round(
            random.uniform(500, 15000), 2
        )
        transactions_last_10min = random.randint(2, 5)
        time_since_last_transaction = round(
            random.uniform(20, 180), 2
        )
        device_is_new = 0
        location_is_unusual = 0
        ip_is_unusual = 0
        is_unusual_time = random.choice([0, 0, 0, 1])
        account_age_days = random.randint(
            365, 10000
        )

    # -----------------------------------------------------
    # New customer
    # -----------------------------------------------------

    elif archetype == "new_customer":
        transaction_amount = round(
            random.uniform(50, 5000), 2
        )
        transactions_last_10min = random.randint(0, 2)
        time_since_last_transaction = round(
            random.uniform(60, 1000), 2
        )
        device_is_new = random.choice([0, 0, 1])
        location_is_unusual = 0
        ip_is_unusual = 0
        is_unusual_time = 0
        account_age_days = random.randint(1, 45)

    # -----------------------------------------------------
    # Returning customer after inactivity
    # -----------------------------------------------------

    elif archetype == "returning_customer":
        transaction_amount = round(
            random.uniform(100, 10000), 2
        )
        transactions_last_10min = random.randint(0, 2)
        time_since_last_transaction = round(
            random.uniform(1500, 10000), 2
        )
        device_is_new = 0
        location_is_unusual = random.choice([0, 0, 0, 1])
        ip_is_unusual = 0
        is_unusual_time = random.choice([0, 0, 1])
        account_age_days = random.randint(
            365, 12000
        )

    # -----------------------------------------------------
    # Device upgrade
    # -----------------------------------------------------

    elif archetype == "device_upgrade":
        transaction_amount = round(
            random.uniform(100, 12000), 2
        )
        transactions_last_10min = random.randint(0, 3)
        time_since_last_transaction = round(
            random.uniform(30, 500), 2
        )
        device_is_new = 1
        location_is_unusual = random.choice([0, 0, 1])
        ip_is_unusual = random.choice([0, 0, 1])
        is_unusual_time = 0
        account_age_days = random.randint(
            120, 12000
        )

    # -----------------------------------------------------
    # High velocity fraud
    # -----------------------------------------------------

    elif archetype == "high_velocity_fraud":
        transaction_amount = round(
            random.uniform(1000, 100000), 2
        )
        transactions_last_10min = random.randint(4, 9)
        time_since_last_transaction = round(
            random.uniform(0.2, 15), 2
        )
        device_is_new = random.choice([0, 1])
        location_is_unusual = random.choice([0, 1])
        ip_is_unusual = random.choice([0, 1])
        is_unusual_time = random.choice([0, 0, 1])
        account_age_days = random.randint(
            30, 10000
        )

    # -----------------------------------------------------
    # Account takeover fraud
    # -----------------------------------------------------

    elif archetype == "account_takeover_fraud":
        transaction_amount = round(
            random.uniform(5000, 250000), 2
        )
        transactions_last_10min = random.randint(1, 5)
        time_since_last_transaction = round(
            random.uniform(0.5, 120), 2
        )
        device_is_new = 1
        location_is_unusual = 1
        ip_is_unusual = 1
        is_unusual_time = random.choice([0, 1])
        account_age_days = random.randint(
            365, 18000
        )

    # -----------------------------------------------------
    # New-account fraud
    # -----------------------------------------------------

    elif archetype == "new_account_fraud":
        transaction_amount = round(
            random.uniform(1000, 100000), 2
        )
        transactions_last_10min = random.randint(1, 4)
        time_since_last_transaction = round(
            random.uniform(20, 600), 2
        )
        device_is_new = random.choice([0, 1])
        location_is_unusual = random.choice([0, 1])
        ip_is_unusual = random.choice([0, 1])
        is_unusual_time = random.choice([0, 1])
        account_age_days = random.randint(1, 25)

    # -----------------------------------------------------
    # Dormant account reactivation fraud
    # -----------------------------------------------------

    else:
        transaction_amount = round(
            random.uniform(3000, 150000), 2
        )
        transactions_last_10min = random.randint(2, 7)
        time_since_last_transaction = round(
            random.uniform(1000, 10000), 2
        )
        device_is_new = random.choice([0, 1])
        location_is_unusual = random.choice([0, 1])
        ip_is_unusual = random.choice([0, 1])
        is_unusual_time = random.choice([0, 1])
        account_age_days = random.randint(
            3650, 18250
        )

    return {
        "transaction_amount": transaction_amount,
        "transactions_last_10min": transactions_last_10min,
        "time_since_last_transaction": time_since_last_transaction,
        "device_is_new": device_is_new,
        "location_is_unusual": location_is_unusual,
        "ip_is_unusual": ip_is_unusual,
        "is_unusual_time": is_unusual_time,
        "account_age_days": account_age_days,
    }