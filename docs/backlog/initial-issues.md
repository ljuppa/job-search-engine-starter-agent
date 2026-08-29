# Initial GitHub Issues

Create these issues in roughly this order.

This is the original high-level issue seed. Use the [delivery backlog](README.md)
for current milestone status and detailed, reviewable stories. M1 is decomposed in
[M1 domain contracts](m1-domain-contracts.md).

## #1 Development environment baseline
Docker Compose starts PostgreSQL, backend, worker, scheduler and frontend; `/health` responds; README setup works on both Macs.

## #2 Define domain contract package
Implement versioned Pydantic contracts for CandidateProfile, ProfileEvidence, ProfileChangeProposal, RawJob, Job, JobProfile, Assessment, Recommendation, UserFeedback and ExecutionContext.

## #3 Persistence skeleton
SQLAlchemy base, DB session, Alembic setup and first schema migration for User/Profile primitives.

## #4 LLM Gateway canonical contracts
Define LLMRequest/LLMResponse, provider capabilities, provider protocol and model registry configuration.

## #5 OpenAI provider adapter
Implement first gateway provider with structured output, normalized usage/latency/error handling and tests using mocks.

## #6 AgentRun observability model
Persist execution metadata and create common AgentRunner abstraction reused by production and evals.

## #7 Profiler v0 interface
Define Profiler input/output contracts and a deterministic/mock implementation before LLM behavior.

## #8 Profiler synthetic eval set
Create initial fact extraction, hard-constraint, inference-discipline and provenance cases.

## #9 OpenAI-backed Profiler extraction
Implement structured initial-profile extraction using frozen input samples and run evals.
