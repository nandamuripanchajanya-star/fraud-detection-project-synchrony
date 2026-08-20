from sqlalchemy import text

from database import SessionLocal
from embedding_service import generate_embedding


def search_fraud_knowledge(
    query: str,
    limit: int = 3
):
    if not query or not query.strip():
        raise ValueError("Search query cannot be empty.")

    if limit < 1 or limit > 10:
        raise ValueError(
            "Limit must be between 1 and 10."
        )

    query_embedding = generate_embedding(query)

    db = SessionLocal()

    try:
        results = db.execute(
            text(
                """
                SELECT
                    id,
                    title,
                    content,
                    source,
                    1 - (embedding <=> CAST(:embedding AS vector))
                    AS similarity
                FROM fraud_knowledge
                ORDER BY embedding <=> CAST(:embedding AS vector)
                LIMIT :limit
                """
            ),
            {
                "embedding": str(query_embedding),
                "limit": limit,
            },
        ).mappings().all()

        return [
            {
                "id": row["id"],
                "title": row["title"],
                "content": row["content"],
                "source": row["source"],
                "similarity": float(row["similarity"]),
            }
            for row in results
        ]

    finally:
        db.close()