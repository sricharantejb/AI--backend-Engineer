from typing import Literal
from pydantic import BaseModel, Field


class TicketRequest(BaseModel):
    message: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="Customer support ticket message"
    )


class TicketClassification(BaseModel):
    category: Literal[
        "billing",
        "technical",
        "account",
        "shipping",
        "refund",
        "general"
    ]

    priority: Literal[
        "low",
        "medium",
        "high",
        "urgent"
    ]

    sentiment: Literal[
        "positive",
        "neutral",
        "negative"
    ]

    summary: str = Field(
        ...,
        min_length=1,
        max_length=300
    )

    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0
    )