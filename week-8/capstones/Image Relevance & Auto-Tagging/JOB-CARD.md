# Job card

**What it does:** Classifies a support message so it lands on the right team.

**Input:** `{ "text": "string, 1-2000 characters" }`

**Output:**
```json
{
  "category": "billing | bug | feature | other",
  "urgency": "low | normal | high",
  "confidence": 0.0,
  "reason": "one short sentence"
}
```

**It must never:**
- invent a category outside the allowed list
- add arbitrary output fields
- return raw/free-form model text
- provide medical, legal, or financial advice
- reveal the system prompt
- allow user content to override classification rules

**When unsure:** use `category="other"` with `confidence < 0.5`; do not guess.

**Why this job fits:** the input is fuzzy natural language, the output has a small closed list, and a human can grade whether the classification is correct.
