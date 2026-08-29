# ADR-003 — Provider-Neutral LLM Gateway

**Status:** Accepted

## Context
Agents require model capabilities, but provider lock-in would leak SDK-specific behavior across the codebase.

## Decision
All LLM access goes through an internal `LLMGateway`. Provider adapters implement a canonical request/response contract. OpenAI is the first adapter.

## Gateway responsibilities
Provider/model routing, structured output, capability checks, retry/timeout policy, usage/cost telemetry, error normalization and prompt/model metadata.

## Consequences
Small abstraction cost now; easier experimentation, fallback and provider changes later.
