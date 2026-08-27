import json
import os
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .client import LLMClient, LLMRequestError, LLMTimeoutError
from .schema import TriageOutput


BASE_DIR = Path(__file__).resolve().parents[2]
PROMPT_PATH = BASE_DIR / "prompts" / "support-ticket-v1.md"
LOG_DIR = BASE_DIR / "logs"
QUARANTINE_PATH = LOG_DIR / "quarantine.jsonl"
COST_LOG_PATH = LOG_DIR / "llm_calls.jsonl"

PROMPT_VERSION = os.getenv("PROMPT_VERSION", "support-ticket-v1")


def load_prompt() -> str:
    return PROMPT_PATH.read_text(encoding="utf-8")


def _extract_json(raw: str) -> dict[str, Any]:
    text = raw.strip()

    # Handle ```json ... ``` or ``` ... ```
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.I)
        text = re.sub(r"\s*```$", "", text)

    # Remove leading prose/trailing prose by selecting the outermost object.
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("Model output did not contain a JSON object")

    return json.loads(text[start : end + 1])


def _validate(raw: str) -> TriageOutput:
    parsed = _extract_json(raw)
    return TriageOutput.model_validate(parsed)


def _log_call(
    *,
    model: str,
    input_tokens: int,
    output_tokens: int,
    duration_ms: int,
    repair_count: int,
) -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    input_rate = float(os.getenv("COST_INPUT_PER_1M_USD", "0"))
    output_rate = float(os.getenv("COST_OUTPUT_PER_1M_USD", "0"))
    estimated_cost = (
        input_tokens / 1_000_000 * input_rate
        + output_tokens / 1_000_000 * output_rate
    )

    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "prompt_version": PROMPT_VERSION,
        "model": model,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "duration_ms": duration_ms,
        "repair_count": repair_count,
        "estimated_cost_usd": round(estimated_cost, 8),
    }

    with COST_LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")

    # Also emit a structured stdout line.
    print("LLM_CALL " + json.dumps(record, separators=(",", ":")))


def _quarantine(input_text: str, raw_output: str, error: str) -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "prompt_version": PROMPT_VERSION,
        "input": input_text,
        "raw_model_output": raw_output[:10000],
        "error": error,
    }
    with QUARANTINE_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")


def deterministic_fallback(text: str) -> TriageOutput:
    lower = text.lower()

    if any(word in lower for word in ("refund", "invoice", "charged", "payment", "bill")):
        category = "billing"
    elif any(word in lower for word in ("bug", "error", "crash", "broken", "fails")):
        category = "bug"
    elif any(word in lower for word in ("feature", "request", "would like", "add")):
        category = "feature"
    else:
        category = "other"

    urgent = any(
        word in lower for word in ("urgent", "asap", "down", "blocked", "critical")
    )

    return TriageOutput(
        category=category,
        urgency="high" if urgent else "normal",
        confidence=0.35,
        reason="AI processing is disabled; deterministic fallback used.",
    )


def _stub_response(text: str) -> TriageOutput:
    lower = text.lower()
    if any(w in lower for w in ("refund", "charged", "invoice", "payment", "bill")):
        category = "billing"
    elif any(w in lower for w in ("bug", "error", "crash", "broken", "fails")):
        category = "bug"
    elif any(w in lower for w in ("feature", "request", "add", "would like")):
        category = "feature"
    else:
        category = "other"

    urgency = "high" if any(w in lower for w in ("urgent", "asap", "down", "blocked")) else "normal"

    return TriageOutput(
        category=category,
        urgency=urgency,
        confidence=0.90 if category != "other" else 0.30,
        reason="Stub response used for deterministic local testing.",
    )


def triage(text: str) -> tuple[TriageOutput, dict[str, Any]]:
    # Kill switch: no model call.
    if os.getenv("LLM_ENABLED", "true").lower() == "false":
        return deterministic_fallback(text), {"model_calls": 0, "repair_count": 0, "fallback": True}

    # Stub: no model call.
    if os.getenv("LLM_STUB", "0") == "1":
        return _stub_response(text), {"model_calls": 0, "repair_count": 0, "stub": True}

    prompt = load_prompt()
    client = LLMClient()

    total_input_tokens = 0
    total_output_tokens = 0
    total_duration = 0
    repair_count = 0
    raw_output = ""

    # Initial model call + at most one repair call.
    for call_number in range(2):
        started = time.perf_counter()

        try:
            if call_number == 0:
                result = client.complete(prompt, text)
            else:
                repair_instruction = (
                    prompt
                    + "\n\nREPAIR TASK:\n"
                    + "Your previous answer was rejected.\n"
                    + "Return ONLY corrected JSON matching the schema.\n"
                    + "Validation error: "
                    + validation_error
                    + "\n"
                    + "Previous answer:\n"
                    + raw_output[:10000]
                )
                result = client.complete(repair_instruction, text)
                repair_count = 1

            raw_output = result["text"]
            total_input_tokens += result["input_tokens"]
            total_output_tokens += result["output_tokens"]
            total_duration += result["duration_ms"]

            try:
                validated = _validate(raw_output)

                _log_call(
                    model=client.model,
                    input_tokens=result["input_tokens"],
                    output_tokens=result["output_tokens"],
                    duration_ms=result["duration_ms"],
                    repair_count=repair_count,
                )

                return validated, {
                    "model_calls": call_number + 1,
                    "repair_count": repair_count,
                    "fallback": False,
                }

            except Exception as exc:
                validation_error = str(exc)
                if call_number == 0:
                    continue

                _quarantine(text, raw_output, validation_error)
                _log_call(
                    model=client.model,
                    input_tokens=result["input_tokens"],
                    output_tokens=result["output_tokens"],
                    duration_ms=result["duration_ms"],
                    repair_count=repair_count,
                )
                raise ValueError(
                    "The model output could not be validated after one repair attempt."
                )

        except LLMTimeoutError:
            raise
        except LLMRequestError:
            raise

    raise ValueError("Model response could not be validated.")
