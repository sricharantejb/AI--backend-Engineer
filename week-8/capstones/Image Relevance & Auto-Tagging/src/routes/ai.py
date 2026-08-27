import os

from fastapi import APIRouter, HTTPException

from src.llm.client import LLMRequestError, LLMTimeoutError
from src.llm.schema import TriageInput, TriageOutput
from src.llm.service import triage


router = APIRouter(tags=["AI"])


@router.post(
    "/triage",
    response_model=TriageOutput,
    responses={
        400: {"description": "Invalid input"},
        422: {"description": "Model output could not be validated"},
        503: {"description": "LLM is unavailable or disabled by provider configuration"},
        504: {"description": "LLM timed out"},
    },
)
def triage_endpoint(payload: TriageInput):
    # Pydantic validates before this function runs, so malformed input
    # never reaches the model.
    try:
        result, _meta = triage(payload.text)
        return result

    except LLMTimeoutError:
        raise HTTPException(
            status_code=504,
            detail="The LLM provider timed out. Please try again later.",
        )

    except LLMRequestError as exc:
        if exc.status_code == 401:
            raise HTTPException(
                status_code=503,
                detail="LLM provider rejected the configured credentials.",
            )
        if exc.status_code in {429, 500, 502, 503, 504}:
            raise HTTPException(
                status_code=503,
                detail="LLM provider is temporarily unavailable.",
            )
        raise HTTPException(
            status_code=503,
            detail="LLM provider request failed.",
        )

    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))

    except Exception:
        # Never leak provider internals or raw model output.
        raise HTTPException(
            status_code=503,
            detail="AI processing failed safely.",
        )
