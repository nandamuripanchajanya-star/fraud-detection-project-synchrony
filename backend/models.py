from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class FraudAssessment(Base):
    __tablename__ = "fraud_assessments"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    transaction_amount: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    transactions_last_10min: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    time_since_last_transaction: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    device_is_new: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    location_is_unusual: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    ip_is_unusual: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    is_unusual_time: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    account_age_days: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    fraud_probability: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    risk_band: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )

    decision: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )

    reasons: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )