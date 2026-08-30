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

**Status:** Done

Implement the first provider adapter with `gpt-5.6-luna`, strict structured
output mapping, `store=False`, normalised errors and mocked tests.

### M2-03 — Retry, timeout and telemetry policy

**Status:** Done

Three attempts use a 30-second per-attempt timeout and exponential backoff from
250 ms with jitter, capped at two seconds. Only normalised retryable errors are
retried. Typed telemetry is emitted through an injected sink.

## Explicitly out of scope

- Agent prompts or agent behaviour.
- Persistence of agent runs. This begins with the later observability story.
- Provider SDK access outside `backend/src/llm/providers/`.
