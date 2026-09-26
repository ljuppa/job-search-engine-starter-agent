# Delivery Backlog

This is the living delivery view for the project. Each milestone gets a focused
backlog before implementation begins. A story moves through `Not started`,
`In progress`, `In review`, and `Done` only when its acceptance criteria are met.

| Milestone | Status | Scope | Backlog |
|---|---|---|---|
| M0 — Development environment | Done | Local services, CI, documentation and developer commands | [Initial issues](initial-issues.md) |
| M1 — Domain contracts | Done | Versioned Pydantic contracts, examples and contract tests | [M1 domain contracts](m1-domain-contracts.md) |
| M2 — LLM Gateway | Done | Gateway, provider adapter and telemetry | [M2 LLM Gateway](m2-llm-gateway.md) |
| M3 — Profiler | Done | Profile extraction, proposals and profiler evals | [M3 Profiler](m3-profiler.md) |
| M4 — Analyst | Done | Raw-job normalization and analyst evals | [M4 Analyst](m4-analyst.md) |
| M5 — Matcher | Not started | Fit assessment and deterministic constraints | To be planned before work begins |
| M6 — Strategist | Not started | Career assessment | To be planned before work begins |
| M7 — Scout | Not started | Connectors, ingestion and deduplication | To be planned before work begins |
| M8 — Orchestrated pipeline | Not started | Queue, workflows, runs and ranking | To be planned before work begins |
| M9 — Basic UI | Not started | Onboarding, shortlist and feedback surfaces | To be planned before work begins |
| M10 — Deployment | Not started | Managed environments and release flow | To be planned before work begins |
| M11 — Real-world evaluation | Not started | Live-market measurement and findings | To be planned before work begins |

## Working agreement

- A story is small enough to review and explain independently.
- Each story states its dependencies and observable acceptance criteria.
- Contract, agent, prompt, and model-routing changes include the relevant tests or evals.
- Before starting a new story, review its scope and obtain human approval under `AGENTS.md`.
- Keep the architecture and roadmap documents aligned when a story changes an architectural decision.
