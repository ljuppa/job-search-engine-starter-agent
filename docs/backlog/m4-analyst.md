# M4 Backlog — Analyst

## Milestone outcome

The application converts one frozen, globally shared `RawJob` into a
versioned `JobProfile` without inventing requirements or missing information.

### M4-01 — Analyst boundary contracts

**Status:** Done

Typed global input, source-grounded facts, and a non-persistent job-profile draft.

### M4-02 — Shared job persistence

**Status:** Done

Persist immutable RawJob and Job snapshots plus versioned JobProfile revisions.

### M4-03 — Deterministic Analyst service

**Status:** Done

Apply system-owned IDs, revision, and timestamps outside LLM output.

### M4-04 — Structured extraction and eval cases

**Status:** Done

Use only LLMGateway and frozen cases for missing-data and unsupported-inference checks.

### M4-05 — Milestone review

**Status:** Done
