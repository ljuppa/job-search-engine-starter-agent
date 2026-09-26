# M8 Backlog — Orchestrated pipeline

## Milestone outcome

Explicit workflows coordinate agents and preserve a complete, reproducible audit
trail without allowing agents to invoke one another.

### M8-01 — Workflow and agent run audit foundation

**Status:** Done

Versioned workflow-state records and immutable agent-run records capture scope,
attribution, references, model/prompt/schema versions, latency, usage and safe
error codes.

### M8-02 — Queue worker and retry policy

**Status:** Done

PostgreSQL queue tasks are claimed with row locking, retry with bounded
deterministic exponential backoff, and are completed or failed explicitly.

### M8-03 — Pipeline orchestration and ranking

**Status:** Done

The pipeline has deterministic assessment ranking and an explicit durable queue
boundary. `JobEvaluationWorkflow` composes Analyst, Matcher and Strategist
without agent-to-agent calls, preserving ADR-004.
