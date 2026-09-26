# M3 Backlog — Profiler

## Milestone outcome

The application can extract candidate-profile information from supplied sources,
ask for missing confirmed constraints, and make auditable change proposals. It
never silently changes a confirmed profile.

## Stories

### M3-01 — Profiler interface and milestone plan

**Status:** Done

Define typed Profiler input, extracted facts, non-persistent change drafts and
candidate questions. The result cannot carry a `CandidateProfile`; deterministic
application code will later convert drafts into canonical pending proposals.

**Acceptance criteria:**

- Input requires a `USER` `ExecutionContext` and references the exact current
  profile revision when one is supplied.
- Sources record provenance; facts and change drafts reference their sources.
- Follow-up-question topics and answer kinds are enumerated.
- Contract tests cover profile scope, revision references, provenance and the
  non-mutating result boundary.

### M3-02 — Profile persistence primitives

**Status:** Done

Add SQLAlchemy and Alembic infrastructure plus repositories and migrations for
candidate profiles, profile evidence and profile change proposals.

### M3-03 — Deterministic Profiler application service

**Status:** Done

Convert Profiler output into a draft profile, canonical evidence and pending
proposals. Confirmed constraints and preferences must never be mutated directly.

### M3-04 — Profiler synthetic eval set and runner

**Status:** Done

Add versioned cases for fact extraction, hard-constraint recall, provenance and
inference discipline, exercised through a reusable deterministic eval runner.

### M3-05 — OpenAI-backed structured extraction

**Status:** Done

Use the M2 `LLMGateway` and logical model registry key to run structured initial
profile extraction against frozen Profiler cases. No Profiler code imports a
provider SDK.

### M3-06 — Follow-up questions and profile confirmation

**Status:** Done

Use deterministic policy to select missing hard-constraint questions. Explicit
answers and accepted proposals create a new profile revision; they do not mutate
an existing revision.

### M3-07 — Milestone review

**Status:** Done

Run tests and evals, review architecture boundaries and update the relevant
documentation before merge.

## Explicitly out of scope

- UI or HTTP onboarding endpoints.
- Job discovery, analysis, matching and ranking.
- Workflow scheduling and cross-agent orchestration.
