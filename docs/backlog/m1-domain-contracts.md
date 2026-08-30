# M1 Backlog — Domain Contracts

## Milestone outcome

The application has one versioned, validated contract language for agents,
workflows, APIs, examples, and evaluations. No agent behavior, database schema,
or LLM integration is implemented in this milestone.

## Design decisions already made

| Decision | Outcome |
|---|---|
| Assessment design | One generic `Assessment` contract with an `assessment_type` discriminator. |
| Profile changes | Low-risk changes may be auto-accepted only by deterministic policy; confirmed constraints and preferences require direct user acceptance. |
| Entity revisions | Revisions are incrementing integers scoped to a stable aggregate ID. |
| Contract sharing | Pydantic models in `backend/src/domain/contracts/` are canonical and are shared by production and eval code. |

## Story map

```text
M1-01 Common primitives
  ├── M1-02 Candidate profile and evidence
  │     └── M1-03 Profile-change proposals
  ├── M1-04 Job intelligence
  ├── M1-05 Assessments, recommendations and feedback
  └── M1-06 Execution context and public exports
        └── M1-07 Example fixtures
              └── M1-08 Contract test suite and milestone review
```

## Stories

### M1-01 — Establish the contract package

**Status:** Done  
**Depends on:** M0

**User story:** As a developer, I want one discoverable package for versioned
domain contracts so every module imports the same definitions.

**Acceptance criteria:**

- `backend/src/domain/contracts/` is the canonical package location.
- Shared primitives define schema version, stable identifiers, aggregate revision,
  timestamps, ownership, and evidence references where applicable.
- Each contract serializes to and validates from JSON without custom caller logic.
- Contracts reject invalid versions, missing required ownership fields, and malformed IDs.
- Unit tests cover the shared primitives and package imports.

### M1-02 — Model candidate profile and evidence

**Status:** Done  
**Depends on:** M1-01

**User story:** As a candidate, I want my career information and the evidence
behind it represented consistently so recommendations can be explained and revised.

**Acceptance criteria:**

- `CandidateProfile` carries `user_id`, stable profile ID, integer revision, schema
  version, status, and the profile fields defined in the data-model architecture.
- `ProfileEvidence` records source type, source reference, captured claim, and confidence.
- Confirmed hard constraints and preferences are represented separately from soft preferences.
- The contract validates that profile revisions are positive integers and private records carry `user_id`.
- Tests cover a valid profile, invalid ownership/version data, and evidence provenance.

### M1-03 — Model profile-change proposals

**Status:** Done  
**Depends on:** M1-02

**User story:** As a candidate, I want inferred profile changes proposed with
evidence rather than silently treated as facts.

**Acceptance criteria:**

- `ProfileChangeProposal` contains the target profile, proposed field/value, prior value,
  rationale, evidence references, confidence, source, and status.
- Supported statuses are `PENDING`, `AUTO_ACCEPTED`, `USER_ACCEPTED`, `REJECTED`, and `SUPERSEDED`.
- The contract makes the proposed change and its provenance explicit; it does not mutate `CandidateProfile`.
- Tests demonstrate valid status values and reject malformed or owner-mismatched proposals.
- The later Profiler policy is explicitly responsible for deciding whether a low-risk proposal may be auto-accepted.

### M1-04 — Model global job intelligence

**Status:** Done
**Depends on:** M1-01

**User story:** As the job-intelligence system, I want raw postings, canonical jobs,
and derived job profiles distinguished so shared source data can be reused safely.

**Acceptance criteria:**

- `RawJob` models immutable source content, source identity, URL, retrieval timestamps, and content hash.
- `Job` models the global canonical identity and references its source records without any `user_id`.
- `JobProfile` models the Analyst-derived structured interpretation with integer revision and confidence/unknown-field support.
- Tests enforce global ownership boundaries and positive job-profile revisions.
- The existing job-profile example fixture validates against the contract after M1-07.

### M1-05 — Model user-specific decisions

**Status:** Done
**Depends on:** M1-01, M1-02, M1-04

**User story:** As a candidate, I want fit, career value, recommendations, and my
feedback captured against the exact profile and job information used.

**Acceptance criteria:**

- `Assessment` uses `assessment_type` to distinguish `FIT` and `CAREER` while retaining one common validated envelope.
- Assessments reference `user_id`, job ID, candidate-profile revision, job-profile revision, score, confidence, evidence, risks/gaps, and agent-run reference.
- `Recommendation` is user-scoped and references the inputs used for its final score, rank, classification, and explanation.
- `UserFeedback` is user-scoped and limits actions to the documented feedback vocabulary.
- Tests reject invalid scores, unknown feedback actions, missing ownership, and unversioned assessment inputs.

### M1-06 — Model execution context and public exports

**Status:** Done
**Depends on:** M1-01, M1-05

**User story:** As a workflow developer, I want a typed execution context and a
stable import surface so every agent run is attributable and easy to integrate.

**Acceptance criteria:**

- `ExecutionContext` includes correlation ID, trace ID, workflow-run ID, `user_id`
  when applicable, profile revision, and job ID when applicable.
- Contracts are exported from a documented package surface rather than imported from private module paths.
- The execution-context example fixture validates against the contract after M1-07.
- Tests cover user-scoped and global-context validation rules.

### M1-07 — Align examples and generated schemas

**Status:** Done
**Depends on:** M1-02, M1-03, M1-04, M1-05, M1-06

**User story:** As a developer and evaluator, I want realistic validated examples
so I can understand each contract and build reliable tests from it.

**Acceptance criteria:**

- Existing JSON examples under `data/schemas/` validate against the canonical Pydantic models.
- Missing examples are added for the remaining M1 contracts.
- Examples use synthetic, non-sensitive data and explicitly state their schema version.
- JSON Schema can be generated from each public Pydantic contract without hand-maintained duplicate schemas.

### M1-08 — Prove the contract boundary

**Status:** Not started  
**Depends on:** M1-01 through M1-07

**User story:** As a maintainer, I want automated proof that contracts remain
compatible and enforce architecture rules before agents begin depending on them.

**Acceptance criteria:**

- Contract tests cover valid JSON round trips, invalid inputs, enum boundaries,
  ownership, revision, and canonical-versus-derived rules.
- The contract suite runs through `make test` and CI.
- The milestone review confirms no provider, persistence, workflow, or agent behavior
  was added beyond contract definitions.
- Documentation links to the contract package and records any approved deviations.

## M1 Definition of Done

- All eight stories are `Done` and their acceptance criteria are met.
- Every public contract has a schema version, validation tests, and a representative synthetic example.
- Production and eval code import the same canonical contract package.
- `make lint` and `make test` pass locally and CI is green.
- The human developer can explain ownership, revision, and proposal-safety rules.

## Explicitly out of scope

- SQLAlchemy models, Alembic configuration, or database migrations.
- Agent implementations, prompts, LLM provider calls, or workflow orchestration.
- Ranking arithmetic, hard-constraint policy execution, deduplication logic, and external connectors.

Persistence begins in the next planned persistence story after M1 contracts are stable.
