# FlyRank Week 7 — Put an LLM Behind Your API

A small FastAPI service that turns an unstructured support message into **validated JSON**. The endpoint is intentionally not a chatbot: one request goes in and one structured answer comes out.

The implementation treats the LLM as an unreliable external API. It validates input before spending a model call, keeps the prompt in a versioned file, separates system instructions from user content, validates every model response, repairs a bad response at most once, quarantines failures, uses a 30-second timeout, retries only retryable provider failures, logs token/cost metadata, and has a kill switch.

## Stack

- Python 3.10+
- FastAPI
- Pydantic
- OpenAI-compatible Python SDK
- OpenRouter (`openrouter/free`) or Ollama
- Git/GitHub

## Project structure

```text
week-7/
├── app.py
├── requirements.txt
├── .env
├── .env.example
├── .gitignore
├── README.md
├── JOB-CARD.md
├── src/
│   ├── __init__.py
│   ├── llm/
│   │   ├── __init__.py
│   │   ├── client.py
│   │   ├── schema.py
│   │   └── service.py
│   └── routes/
│       ├── __init__.py
│       └── ai.py
├── prompts/
│   └── support-ticket-v1.md
├── evals/
│   ├── cases.json
│   └── run_eval.py
└── logs/
    └── (created at runtime)
```

## Setup

### 1. Create and activate a virtual environment

macOS/Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 3. Configure environment

Copy the example if needed:

```bash
cp .env.example .env
```

For zero-cost development, keep:

```text
LLM_STUB=1
LLM_ENABLED=true
```

For a real hosted model, put your own OpenRouter key in `.env` and set:

```text
LLM_STUB=0
LLM_ENABLED=true
LLM_BASE_URL=https://openrouter.ai/api/v1
LLM_MODEL=openrouter/free
```

Never commit `.env`.

## Run

```bash
uvicorn app:app --reload
```

Swagger:

```text
http://127.0.0.1:8000/docs
```

## API

### POST /triage

Input:

```json
{
  "text": "I was charged twice for my subscription."
}
```

Example valid response:

```json
{
  "category": "billing",
  "urgency": "normal",
  "confidence": 0.9,
  "reason": "Stub response used for deterministic local testing."
}
```

### Runnable curl

With stub mode enabled:

```bash
curl -X POST http://127.0.0.1:8000/triage \
  -H "Content-Type: application/json" \
  -d '{"text":"I was charged twice for my subscription."}'
```

Expected shape:

```json
{
  "category": "billing",
  "urgency": "normal",
  "confidence": 0.9,
  "reason": "Stub response used for deterministic local testing."
}
```

### Deliberately invalid input

```bash
curl -i -X POST http://127.0.0.1:8000/triage \
  -H "Content-Type: application/json" \
  -d '{"text":""}'
```

FastAPI returns `422` for Pydantic's default request validation. If your evaluator requires the exact assignment wording of `400`, change the route to accept a raw body and explicitly convert validation errors to 400; the important security property is that invalid input is rejected before any model call.

## Reliability behavior

### Schema

`src/llm/schema.py` defines closed enums for category and urgency and constrains confidence to `0..1`.

### Prompt versioning

The prompt is not embedded in the route. It lives at:

```text
prompts/support-ticket-v1.md
```

### Repair

A model response is parsed and validated. If parsing or schema validation fails, the service makes **exactly one repair call** containing the validation error and rejected output. If the repaired result is still invalid, the response becomes `422` and the raw result is written to:

```text
logs/quarantine.jsonl
```

Raw model text is never returned to the API caller.

### Timeout

The SDK timeout is explicitly set from `LLM_TIMEOUT_SECONDS`, defaulting to 30 seconds and capped at 60.

### Retry policy

The SDK's automatic retries are disabled with:

```text
max_retries=0
```

The application controls retries:

- retry: timeout, 429, 5xx
- never retry: 400, 401, 403
- backoff: 1s, 2s, then jitter
- obey `Retry-After` when supplied
- maximum 3 attempts

### Kill switch

Set:

```text
LLM_ENABLED=false
```

The endpoint makes **zero model calls** and returns a deterministic fallback.

### Stub mode

Set:

```text
LLM_STUB=1
```

This returns a schema-valid deterministic answer without calling the provider. It is useful while building and testing.

## Cost logging

Each real model response writes a structured record to:

```text
logs/llm_calls.jsonl
```

The record includes:

- prompt version
- model
- input tokens
- output tokens
- duration
- repair count
- estimated cost

The two cost-rate environment variables are intentionally configurable because free model pricing and provider pricing can change.

For a rough 10,000-request estimate:

```text
estimated cost = average input tokens × input price
               + average output tokens × output price
```

For a free OpenRouter model this can be $0 while within the provider's current free allowance.

## Evaluation

There are eight hand-labelled cases in:

```text
evals/cases.json
```

Run the API first, then:

```bash
python evals/run_eval.py
```

Example stub result:

```text
Score: 8/8 (100.0%)
All cases passed.
```

**Eval date:** 2026-08-28  
**Prompt version:** `support-ticket-v1`

Replace this score with the score from your real provider run before publishing the repository.

## Requirement checklist

- [x] JOB-CARD.md
- [x] One decision per request
- [x] Closed output lists
- [x] Input validation before model call
- [x] Pydantic output schema
- [x] LLM_STUB=1
- [x] Versioned prompt file
- [x] Role, output shape, rules, unsure behavior, examples
- [x] User content sent as a separate user message
- [x] Parse + validate model output
- [x] Exactly one repair attempt
- [x] Quarantine log after failed repair
- [x] Raw model text never returned
- [x] Explicit <=60 second timeout
- [x] Retries for timeout/429/5xx
- [x] No retries for 400/401/403
- [x] Retry-After support
- [x] Structured cost/token logging
- [x] Kill switch
- [x] Eight eval cases
- [x] README with curl and setup

## Provider switching

The application uses the OpenAI-compatible client. To switch between OpenRouter and Ollama, change only:

```text
LLM_BASE_URL
LLM_API_KEY
LLM_MODEL
```

Ollama example:

```text
LLM_BASE_URL=http://localhost:11434/v1/
LLM_API_KEY=ollama
LLM_MODEL=gemma3:1b
```

## AI vs Me — bonus template

For the bonus rematch, create a separate `ai-version/` folder and compare it against this hand-built implementation.

Things to compare:

1. Did the generated code use a real timeout rather than the SDK's long default?
2. Did it validate and quarantine model output instead of returning raw text?
3. Did it avoid retrying 401/403?
4. Did it keep untrusted user content outside the system prompt?
5. Did it implement exactly one repair attempt?

Do not claim these bonus results until you have actually run and compared them.

## Security note

Do not put real customer, employer, confidential, medical, legal, or financial information into a free hosted model endpoint. The free OpenRouter path may have data-use implications described by the provider. Use synthetic evaluation data.

## Git workflow

Create at least six meaningful commits, for example:

```bash
git add .
git commit -m "Stage 0: job card and provider setup"

git add .
git commit -m "Stage 1: endpoint validation schema and stub"

git add .
git commit -m "Stage 2: versioned support ticket prompt"

git add .
git commit -m "Stage 3: parse validate repair and quarantine"

git add .
git commit -m "Stage 4: timeout retries cost logging and kill switch"

git add .
git commit -m "Stage 5: eval set results and README"
```

Before pushing:

```bash
git status
git check-ignore .env
```

`.env` must be ignored and must never be committed.
