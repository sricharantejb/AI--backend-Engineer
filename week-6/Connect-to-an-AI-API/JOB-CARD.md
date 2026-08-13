# Job Card — AI Support Ticket Classifier

## Problem

Customer support messages need to be classified before they can be routed to the appropriate workflow.

Doing this manually is slow and inconsistent.

## AI Task

Use an LLM to classify each support ticket.

## Input

A plain-text customer support message.

## Output

Structured JSON:

- category
- priority
- sentiment
- summary
- confidence

## Categories

- billing
- technical
- account
- shipping
- refund
- general

## Reliability Requirements

The application must:

- validate incoming input
- use a defined output schema
- reject invalid model output
- use a request timeout
- retry failed requests
- stop retrying after a limited number of attempts
- avoid exposing the API key
- provide deterministic model settings
- evaluate the model using eight test cases

## Endpoint

POST `/ai/classify`

## Example Input

```json
{
  "message": "I was charged twice for my order."
}