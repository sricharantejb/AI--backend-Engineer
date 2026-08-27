import os
import time
import random
from typing import Any

from openai import OpenAI


RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}
NON_RETRYABLE_STATUS_CODES = {400, 401, 403}


class LLMTimeoutError(Exception):
    pass


class LLMRequestError(Exception):
    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


def _status_code(exc: Exception) -> int | None:
    return getattr(exc, "status_code", None) or getattr(exc, "status", None)


def _retry_after(exc: Exception) -> float | None:
    response = getattr(exc, "response", None)
    headers = getattr(response, "headers", None)
    if not headers:
        return None
    value = headers.get("retry-after") or headers.get("Retry-After")
    if not value:
        return None
    try:
        return max(0.0, float(value))
    except (TypeError, ValueError):
        return None


class LLMClient:
    def __init__(self) -> None:
        self.base_url = os.getenv("LLM_BASE_URL", "https://openrouter.ai/api/v1")
        self.api_key = os.getenv("LLM_API_KEY", "")
        self.model = os.getenv("LLM_MODEL", "openrouter/free")
        self.timeout = min(float(os.getenv("LLM_TIMEOUT_SECONDS", "30")), 60.0)
        self.max_attempts = max(1, min(int(os.getenv("LLM_MAX_ATTEMPTS", "3")), 3))

        self.client = OpenAI(
            base_url=self.base_url,
            api_key=self.api_key,
            timeout=self.timeout,
            max_retries=0,  # retries are controlled here explicitly
        )

    def complete(self, system_prompt: str, user_text: str) -> dict[str, Any]:
        """
        Calls an OpenAI-compatible provider.
        Retries only timeout/429/5xx, with exponential backoff and jitter.
        """
        last_exc: Exception | None = None

        for attempt in range(1, self.max_attempts + 1):
            started = time.perf_counter()
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        # Untrusted user content stays in a separate user message.
                        {"role": "user", "content": user_text},
                    ],
                    temperature=0.0,
                )

                elapsed_ms = int((time.perf_counter() - started) * 1000)
                message = response.choices[0].message.content or ""
                usage = response.usage

                input_tokens = int(getattr(usage, "prompt_tokens", 0) or 0)
                output_tokens = int(getattr(usage, "completion_tokens", 0) or 0)

                return {
                    "text": message,
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "duration_ms": elapsed_ms,
                    "attempt": attempt,
                }

            except Exception as exc:
                last_exc = exc
                code = _status_code(exc)

                # Authentication/bad-request/permission errors are never retried.
                if code in NON_RETRYABLE_STATUS_CODES:
                    raise LLMRequestError(str(exc), code) from exc

                retryable = isinstance(exc, TimeoutError) or (
                    code in RETRYABLE_STATUS_CODES
                )

                # OpenAI SDK timeout exceptions may not inherit built-in TimeoutError.
                if "timeout" in exc.__class__.__name__.lower():
                    retryable = True

                if not retryable or attempt >= self.max_attempts:
                    if retryable and "timeout" in str(exc).lower():
                        raise LLMTimeoutError(str(exc)) from exc
                    raise LLMRequestError(str(exc), code) from exc

                wait = _retry_after(exc)
                if wait is None:
                    wait = (2 ** (attempt - 1)) + random.uniform(0, 0.25)

                time.sleep(wait)

        raise LLMRequestError(str(last_exc or "LLM request failed"))
