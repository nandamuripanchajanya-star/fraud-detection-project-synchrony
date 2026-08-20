from database import SessionLocal
from embedding_service import generate_embedding
from sqlalchemy import text


KNOWLEDGE = [
    {
        "title": "High velocity activity",
        "content": (
            "A sudden burst of multiple transactions within a short "
            "time window can indicate automated abuse, account takeover, "
            "or fraudulent transaction activity. High transaction velocity "
            "should be evaluated together with other behavioral signals."
        ),
        "source": "Fraud detection knowledge base",
    },
    {
        "title": "New device risk",
        "content": (
            "A transaction from a newly observed device can increase fraud "
            "risk, especially when combined with unusual location, unusual "
            "network information, or other anomalous account behavior."
        ),
        "source": "Fraud detection knowledge base",
    },
    {
        "title": "Unusual location",
        "content": (
            "A transaction originating from an unusual geographic location "
            "can be a fraud indicator. The signal is stronger when it occurs "
            "together with a new device or unusual network context."
        ),
        "source": "Fraud detection knowledge base",
    },
    {
        "title": "Unusual IP or network",
        "content": (
            "An unfamiliar or anomalous network or IP context can indicate "
            "account compromise or suspicious transaction activity. It should "
            "be interpreted alongside device and behavioral signals."
        ),
        "source": "Fraud detection knowledge base",
    },
    {
        "title": "New account transaction",
        "content": (
            "Transactions on very recently created accounts can require "
            "additional scrutiny, particularly when transaction amounts are "
            "high or multiple behavioral anomalies are present."
        ),
        "source": "Fraud detection knowledge base",
    },
    {
        "title": "Account takeover pattern",
        "content": (
            "A combination of a new device, unusual location, unusual network, "
            "and rapid transaction activity can be consistent with an account "
            "takeover scenario."
        ),
        "source": "Fraud detection knowledge base",
    },
]


def seed_knowledge():
    db = SessionLocal()

    try:
        existing_count = db.execute(
            text("SELECT COUNT(*) FROM fraud_knowledge")
        ).scalar()

        if existing_count > 0:
            print(
                f"Knowledge table already contains "
                f"{existing_count} records."
            )
            return

        for item in KNOWLEDGE:
            embedding = generate_embedding(
                f"{item['title']}. {item['content']}"
            )

            db.execute(
                text(
                    """
                    INSERT INTO fraud_knowledge
                        (title, content, source, embedding)
                    VALUES
                        (:title, :content, :source, :embedding)
                    """
                ),
                {
                    "title": item["title"],
                    "content": item["content"],
                    "source": item["source"],
                    "embedding": str(embedding),
                },
            )

        db.commit()

        print(
            f"Inserted {len(KNOWLEDGE)} knowledge records."
        )

    finally:
        db.close()


if __name__ == "__main__":
    seed_knowledge()