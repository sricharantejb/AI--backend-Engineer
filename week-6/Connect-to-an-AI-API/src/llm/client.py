import os
import time

from dotenv import load_dotenv
from groq import Groq


load_dotenv()


GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv(
    "GROQ_MODEL",
    "llama-3.3-70b-versatile"
)

LLM_TIMEOUT = float(
    os.getenv("LLM_TIMEOUT", "20")
)

LLM_MAX_RETRIES = int(
    os.getenv("LLM_MAX_RETRIES", "2")
)


if not GROQ_API_KEY:
    raise RuntimeError(
        "GROQ_API_KEY is missing. "
        "Add it to your .env file."
    )


client = Groq(
    api_key=GROQ_API_KEY,
    timeout=LLM_TIMEOUT
)


def call_llm(system_prompt: str, user_message: str) -> str:
    """
    Send a request to the LLM.

    Retries are limited so a failing request does not
    continue forever.
    """

    last_error = None

    for attempt in range(LLM_MAX_RETRIES + 1):

        try:
            response = client.chat.completions.create(
                model=GROQ_MODEL,

                messages=[
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": user_message
                    }
                ],

                temperature=0,

                response_format={
                    "type": "json_object"
                }
            )

            content = response.choices[0].message.content

            if not content:
                raise ValueError(
                    "LLM returned an empty response"
                )

            return content

        except Exception as error:

            last_error = error

            if attempt >= LLM_MAX_RETRIES:
                break

            # Exponential backoff
            wait_time = 2 ** attempt

            time.sleep(wait_time)

    raise RuntimeError(
        f"LLM request failed after "
        f"{LLM_MAX_RETRIES + 1} attempts: {last_error}"
    )