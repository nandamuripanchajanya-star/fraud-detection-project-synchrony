import re
from explanation_engine import generate_explanation
from guardrails import validate_llm_response
from llm_service import generate_llm_response
from prompt_templates import build_fraud_investigation_prompt
from schemas import FraudEvent
from semantic_search import search_fraud_knowledge


def generate_investigation_summary(
    event: dict,
    fraud_probability: float,
    risk_band: str,
    decision: str,
):
    event_model = FraudEvent(**event)

    # Generate model-derived reasons for the investigation.
    reasons = generate_explanation(event_model)

    # Build a more investigation-specific semantic-search query.
    #
    # The query now includes:
    # - risk band
    # - model decision
    # - transaction amount
    # - transaction velocity
    # - time since previous transaction
    # - account age
    # - behavioral anomaly signals
    # - model-derived reasons
    #
    # This makes the retrieved fraud knowledge more relevant
    # to the actual transaction being investigated.
    search_query = (
        " ".join(
            [
                "fraud investigation",
                f"risk band {risk_band}",
                f"decision {decision}",
                f"transaction amount {event.get('transaction_amount')}",
                f"transactions last 10 minutes "
                f"{event.get('transactions_last_10min')}",
                f"time since previous transaction "
                f"{event.get('time_since_last_transaction')}",
                f"account age days {event.get('account_age_days')}",
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
                *reasons,
            ]
        )
    )

    # Retrieve the most relevant fraud knowledge.
    knowledge_results = search_fraud_knowledge(
        search_query,
        limit=3,
    )

    # Build the grounded investigation prompt using:
    # transaction signals + model assessment + model reasons
    # + retrieved fraud knowledge.
    prompt = build_fraud_investigation_prompt(
        event=event,
        fraud_probability=fraud_probability,
        risk_band=risk_band,
        decision=decision,
        reasons=reasons,
        knowledge_results=knowledge_results,
    )

    # Generate the LLM investigation.
    llm_response = generate_llm_response(
        prompt
    )

    # Validate the LLM response against application guardrails.
    # The existing model decision remains authoritative.
    def clean_llm_response(text: str) -> str:
        cleaned = text.replace("**", "")
        cleaned = cleaned.replace("__", "")
        cleaned = cleaned.replace("`", "")

        cleaned = re.sub(
            r"(?m)^\s*#+\s*",
            "",
            cleaned,
        )

        return cleaned.strip()
    cleaned_response = clean_llm_response(
        llm_response
    )

    validated_response = validate_llm_response(
        cleaned_response,
        decision,
    )

    return {
        "summary": validated_response,
        "knowledge": knowledge_results,
    }