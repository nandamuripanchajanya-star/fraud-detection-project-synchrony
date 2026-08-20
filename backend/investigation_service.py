from explanation_engine import generate_explanation
from guardrails import validate_llm_response
from llm_service import generate_llm_response
from prompt_templates import (
    build_fraud_investigation_prompt,
)
from schemas import FraudEvent
from semantic_search import search_fraud_knowledge


def generate_investigation_summary(
    event: dict,
    fraud_probability: float,
    risk_band: str,
    decision: str,
):
    event_model = FraudEvent(**event)
    reasons = generate_explanation(event_model)

    search_query = (
        " ".join(
            [
                "fraud risk",
                f"transaction amount {event.get('transaction_amount')}",
                f"transactions {event.get('transactions_last_10min')}",
                "new device"
                if event.get("device_is_new")
                else "",
                "unusual location"
                if event.get("location_is_unusual")
                else "",
                "unusual IP network"
                if event.get("ip_is_unusual")
                else "",
                "unusual time"
                if event.get("is_unusual_time")
                else "",
            ]
        )
    )

    knowledge_results = search_fraud_knowledge(
        search_query,
        limit=3,
    )

    prompt = build_fraud_investigation_prompt(
        event=event,
        fraud_probability=fraud_probability,
        risk_band=risk_band,
        decision=decision,
        reasons=reasons,
        knowledge_results=knowledge_results,
    )

    llm_response = generate_llm_response(
        prompt
    )

    validated_response = validate_llm_response(
        llm_response,
        decision,
    )

    return {
        "summary": validated_response,
        "knowledge": knowledge_results,
    }