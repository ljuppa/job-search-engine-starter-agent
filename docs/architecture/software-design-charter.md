# Software Design Charter — v0.1

## Architecture goal

Build a reliable, explainable system that can continuously discover, understand and rank jobs while remaining simple enough for one developer to operate and learn from.

## Major decisions

1. **Modular monolith first.** Five agents are logical modules, not independently deployed microservices.
2. **Explicit orchestration.** Agents do not invoke other agents directly.
3. **Structured contracts.** Versioned Pydantic/domain objects are all major boundaries.
4. **PostgreSQL system of record.** Avoid additional datastores until justified.
5. **Canonical vs derived state.** Candidate facts/raw source data are canonical; analysis, assessments and ranking can be recomputed.
6. **Version reasoning inputs.** Record agent, prompt, schema, model and input versions.
7. **Asynchronous workflow execution.** API remains responsive; workers execute long-running work.
8. **Provider-neutral LLM Gateway.** OpenAI is the first adapter only.
9. **Deterministic ranking and hard constraints.** No LLM controls arithmetic or hard policy enforcement.
10. **Profile proposal model.** Inferred changes are proposed/confirmed rather than silently committed.
11. **Connector-based Scout.** Greenhouse/Lever/Workday/etc. logic is isolated behind connectors.
12. **Independent deduplication domain service.** Raw source records map to canonical jobs.
13. **Evaluation as first-class architecture.** Production and eval execution use the same agent runner/contracts.

## Logical modules

```text
api/
domain/
agents/
workflows/
integrations/
llm/
persistence/
policies/
evals/
observability/
```

## Guardrails

- no agent-to-agent direct invocation
- no arbitrary agent DB writes
- no silent hard-constraint changes
- no provider calls outside the LLM Gateway
- no business rules buried in prompts
- no LLM ranking arithmetic
- no source-specific crawling logic inside Scout itself
