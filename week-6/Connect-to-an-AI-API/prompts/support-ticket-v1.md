# Support Ticket Classifier v1

## Purpose

Classify customer support messages into a small set of structured categories.

## Categories

- billing
- technical
- account
- shipping
- refund
- general

## Priority

- low
- medium
- high
- urgent

## Sentiment

- positive
- neutral
- negative

## Output

The model must return JSON containing:

- category
- priority
- sentiment
- summary
- confidence

## Rules

1. Return valid JSON only.
2. Do not return Markdown.
3. Do not add extra fields.
4. Confidence must be between 0 and 1.
5. Do not invent information.
6. Keep the summary short.
7. Use temperature 0 for deterministic classification.

## Example

Input:

"My payment was charged twice for the same order."

Expected classification:

```json
{
  "category": "billing",
  "priority": "high",
  "sentiment": "negative",
  "summary": "Customer reports being charged twice for the same order.",
  "confidence": 0.95
}