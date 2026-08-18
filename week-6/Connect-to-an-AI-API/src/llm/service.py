import json

from src.llm.client import call_llm
from src.llm.schema import TicketClassification


SYSTEM_PROMPT = """
You are a customer support ticket classification system.

Your job is to classify the customer's support message.

Return ONLY valid JSON.

The JSON must contain exactly these fields:

{
    "category": "billing | technical | account | shipping | refund | general",
    "priority": "low | medium | high | urgent",
    "sentiment": "positive | neutral | negative",
    "summary": "short summary of the issue",
    "confidence": 0.0
}

Rules:

1. category must be one of:
   billing
   technical
   account
   shipping
   refund
   general

2. priority must be one of:
   low
   medium
   high
   urgent

3. sentiment must be one of:
   positive
   neutral
   negative

4. summary must be short and factual.

5. confidence must be a number between 0 and 1.

6. Do not include markdown.

7. Do not include additional fields.

8. Do not invent facts that are not present in the message.
"""


def classify_ticket(message: str) -> TicketClassification:

    raw_response = call_llm(
        SYSTEM_PROMPT,
        message
    )

    try:

        data = json.loads(raw_response)

    except json.JSONDecodeError as error:

        raise ValueError(
            f"LLM returned invalid JSON: {error}"
        )

    try:

        result = TicketClassification.model_validate(
            data
        )

    except Exception as error:

        raise ValueError(
            f"LLM response failed schema validation: {error}"
        )

    return result