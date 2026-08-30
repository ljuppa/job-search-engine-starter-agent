# M2 Backlog — LLM Gateway

## Milestone outcome

The application accesses LLMs only through a provider-neutral gateway with
typed requests, structured responses, capability routing and normalised errors.

## Stories

### M2-01 — Canonical gateway contracts and model registry

**Status:** Done

**Acceptance criteria:**

- `LLMRequest`, `LLMResponse`, messages, usage and capabilities are typed.
- Requests select a version-controlled logical model key, never a provider model ID.
- A typed `ModelRegistry` rejects unknown models and missing capabilities.
- The gateway returns normalised structured output or raises typed normalised errors.
- Unit tests use a fake provider and make no network calls.

### M2-02 — OpenAI adapter

**Status:** Not started

Implement the first provider adapter with the selected OpenAI model, structured
output mapping, normalised errors and mocked tests.

### M2-03 — Retry, timeout and telemetry policy

**Status:** Not started

Add explicit retry/timeout policy, latency and usage emission, and model-routing
metadata. No retryable provider call may bypass this policy.

## Explicitly out of scope

- Agent prompts or agent behaviour.
- Persistence of agent runs. This begins with the later observability story.
- Provider SDK access outside `backend/src/llm/providers/`.
