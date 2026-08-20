from semantic_search import search_fraud_knowledge


def test_semantic_search_returns_results():
    results = search_fraud_knowledge(
        "new device and suspicious network activity",
        limit=3,
    )

    assert len(results) > 0
    assert len(results) <= 3


def test_semantic_search_results_have_expected_fields():
    results = search_fraud_knowledge(
        "unusual IP address during transaction",
        limit=3,
    )

    assert len(results) > 0

    first = results[0]

    assert "id" in first
    assert "title" in first
    assert "content" in first
    assert "similarity" in first


def test_semantic_search_results_are_ranked():
    results = search_fraud_knowledge(
        "new device and suspicious network activity",
        limit=3,
    )

    similarities = [
        result["similarity"]
        for result in results
    ]

    assert similarities == sorted(
        similarities,
        reverse=True,
    )