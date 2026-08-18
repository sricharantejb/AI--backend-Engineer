from fastapi import APIRouter, HTTPException

from src.llm.schema import (
    TicketRequest,
    TicketClassification
)

from src.llm.service import classify_ticket


router = APIRouter(
    prefix="/ai",
    tags=["AI"]
)


@router.post(
    "/classify",
    response_model=TicketClassification
)
def classify_support_ticket(
    request: TicketRequest
):

    try:

        result = classify_ticket(
            request.message
        )

        return result

    except ValueError as error:

        raise HTTPException(
            status_code=502,
            detail=str(error)
        )

    except RuntimeError as error:

        raise HTTPException(
            status_code=503,
            detail=str(error)
        )

    except Exception:

        raise HTTPException(
            status_code=500,
            detail="Unexpected AI service error"
        )