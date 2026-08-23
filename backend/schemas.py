from pydantic import BaseModel, Field, field_validator, model_validator


class FraudEvent(BaseModel):
    """
    Input received by the real-time fraud detection API.
    Derived features are calculated by the backend.
    """

    transaction_amount: float = Field(
        ...,
        gt=0,
        le=500000,
        description="Amount involved in the current digital-lending event"
    )

    transactions_last_10min: int = Field(
        ...,
        ge=0,
        le=10,
        description="Number of events from the same account in the previous 10 minutes"
    )

    time_since_last_transaction: float = Field(
        ...,
        ge=0.1,
        le=5256000,
        description="Minutes since the previous event"
    )

    device_is_new: int = Field(
        ...,
        ge=0,
        le=1
    )

    location_is_unusual: int = Field(
        ...,
        ge=0,
        le=1
    )

    ip_is_unusual: int = Field(
        ...,
        ge=0,
        le=1
    )

    is_unusual_time: int = Field(
        ...,
        ge=0,
        le=1
    )

    account_age_days: int = Field(
        ...,
        ge=1,
        le=18250
    )

    @field_validator(
        "device_is_new",
        "location_is_unusual",
        "ip_is_unusual",
        "is_unusual_time"
    )
    @classmethod
    def validate_binary_fields(cls, value: int) -> int:
        if value not in (0, 1):
            raise ValueError("Value must be either 0 or 1")

        return value
    @model_validator(mode="after")
    def validate_event_consistency(self):
        # If there were transactions in the last 10 minutes,
        # the previous event must be 1–10 minutes ago.
        if self.transactions_last_10min > 0:
            if not (
                self.time_since_last_transaction >= 1
                and self.time_since_last_transaction <= 10
            ):
                raise ValueError(
                    "When transactions_last_10min is greater than 0, "
                    "time_since_last_transaction must be between "
                    "1 and 10 minutes."
                )

        # Time since previous event cannot exceed account age.
        if self.time_since_last_transaction > self.account_age_days * 1440:
            raise ValueError(
                "Time since previous event cannot exceed account age."
            )

        return self