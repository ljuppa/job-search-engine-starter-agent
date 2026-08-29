# AGENTS.md — Job Search Engine

## Purpose

This repository is both a production-oriented learning project and a portfolio artifact. The human developer owns product decisions, architecture, acceptance criteria, review and merges. AI agents may assist with design, implementation, tests, refactoring and documentation.

## Architecture rules

1. The application is a **modular monolith with asynchronous workers** for v0.1.
2. The five logical agents are Profiler, Scout, Analyst, Matcher and Strategist.
3. Agents **must not call other agents directly**. Workflow orchestration is explicit.
4. All agent boundaries use **versioned structured contracts**, never prose-only contracts.
5. PostgreSQL is the system of record.
6. Canonical data and derived data must remain separate.
7. All LLM calls go through `LLMGateway`; no agent may depend directly on OpenAI or another provider SDK.
8. OpenAI is the initial provider adapter, but the gateway must remain provider-neutral.
9. Hard constraints, ranking arithmetic, workflow state and deduplication are deterministic code.
10. Agents may not silently mutate confirmed user profile constraints or preferences.
11. Every agent execution records model, prompt version, schema version, inputs, output reference, latency, usage and errors.
12. Shared job intelligence is global; user profile, assessments, recommendations and feedback are user-scoped.
13. Private records carry `user_id` from day one even though v0.1 behavior is single-user.
14. Agents must remain stateless across executions; state lives in persistence.

## Development rules

- Prefer small vertical slices over large autonomous implementations.
- Before coding, inspect relevant docs and state the affected contracts/modules.
- Do not introduce dependencies without explaining why they are needed.
- Use Python type hints and Pydantic at external/domain boundaries.
- Add or update tests for every domain behavior change.
- Add eval coverage when changing agent prompts, model routing or reasoning behavior.
- Keep provider-specific code inside `backend/src/llm/providers/`.
- Keep source-specific job integration code inside `backend/src/integrations/`.
- Do not put business rules into prompts if deterministic code can enforce them.
- Never commit secrets or `.env` files.

## Human-in-the-loop gates

For meaningful features:

1. Requirement / issue defined.
2. Codex proposes implementation approach.
3. Human approves or modifies the approach.
4. Codex implements limited scope.
5. Tests/evals run.
6. Codex performs review for correctness and architectural violations.
7. Human can explain the implementation.
8. Human approves merge.

## Definition of Done

A feature is done when:

- acceptance criteria are satisfied;
- implementation is understood by the human developer;
- tests pass;
- relevant evals pass;
- architecture boundaries are respected;
- relevant docs/ADR are updated;
- no unexplained dependency was introduced;
- CI is green;
- PR is reviewed before merge.

## Initial implementation order

Do not start by building web crawlers.

1. Repository/development environment
2. Domain contracts and data model
3. LLM Gateway + OpenAI adapter
4. Profiler + profiler evals
5. Analyst + analyst evals
6. Matcher
7. Strategist
8. Scout/connectors
9. Orchestrated pipeline
10. Basic UI
11. Test deployment
12. Production deployment and real-world evaluation
