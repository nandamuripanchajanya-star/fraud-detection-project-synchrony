def build_fraud_investigation_prompt(
    event: dict,
    fraud_probability: float,
    risk_band: str,
    decision: str,
    reasons: list[str],
    knowledge_results: list[dict],
) -> str:

    knowledge_text = "\n".join(
        [
            (
                f"- {item['title']} "
                f"(similarity: {item['similarity']:.3f})\n"
                f"  {item['content']}"
            )
            for item in knowledge_results
        ]
    )

    reasons_text = "\n".join(
        f"- {reason}"
        for reason in reasons
    )

    return f"""
You are a fraud-risk investigation assistant.

Your job is to explain an existing fraud model decision.
Do not override the model decision.
Do not invent transaction facts.
Do not claim certainty about fraud.

MODEL ASSESSMENT
Fraud probability: {fraud_probability:.4f}
Risk band: {risk_band}
Decision: {decision}

TRANSACTION SIGNALS
Transaction amount (currency not specified): {event.get("transaction_amount")}
Transactions in last 10 minutes: {event.get("transactions_last_10min")}
Time since previous transaction: {event.get("time_since_last_transaction")}
New device: {event.get("device_is_new")}
Unusual location: {event.get("location_is_unusual")}
Unusual IP/network: {event.get("ip_is_unusual")}
Unusual time: {event.get("is_unusual_time")}
Account age days: {event.get("account_age_days")}

MODEL REASONS
{reasons_text}

RELEVANT FRAUD KNOWLEDGE
{knowledge_text}

TASK

Provide a concise investigation summary with exactly these sections:

Risk assessment:
Why it was flagged:
Relevant evidence:
Recommended action:

Rules:
- Base the explanation only on the supplied assessment and knowledge.
- Treat transaction signals as factual inputs, not assumptions.
- Do not invent missing information.
- Do not infer customer identity, location details, merchant details, or intent that are not supplied.
- Do not infer, add, or assume a currency symbol or currency name unless the input explicitly provides one.
- Report monetary values exactly as supplied.
- Do not change APPROVE, REVIEW, or BLOCK.
- State uncertainty where appropriate.
- Keep the response professional and concise.
- Always include the appropriate unit when reporting numerical evidence.
- State transaction amounts as numeric values without inventing a currency.
- State transaction velocity as transactions per 10 minutes.
- State time since previous transaction with its unit, and when helpful include an equivalent unit in parentheses.
- State account age with its unit, and when helpful include an equivalent unit in parentheses.
- Never report a bare numerical value when the meaning depends on a unit.
- Use plain text headings only.
- Do not use Markdown formatting.
- Do not use asterisks (* or **), underscores, hash symbols (#), backticks, or Markdown heading syntax.
- Use these exact plain-text headings:
  Risk assessment:
  Why it was flagged:
  Relevant evidence:
  Recommended action:
""".strip()