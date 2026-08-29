# Milestones

## M0 — Repository and development environment
Docker Compose, backend/frontend scaffolds, GitHub Actions, README, AGENTS.md, documentation baseline.

## M1 — Domain contracts
CandidateProfile, Evidence, ProfileChangeProposal, RawJob, Job, JobProfile, Assessment, Recommendation, Feedback and ExecutionContext schemas.

## M2 — LLM Gateway
Provider-neutral gateway, capability/model registry, OpenAI adapter, retries, structured output, telemetry and unit tests.

## M3 — Profiler
Adaptive profile extraction/conversation, proposal/confirmation model, persistence and Profiler evals.

## M4 — Analyst
Frozen RawJob → JobProfile pipeline and Analyst evals.

## M5 — Matcher
FitAssessment, deterministic hard-constraint policy and matcher evals.

## M6 — Strategist
CareerAssessment based on declared goals, risks and future optionality; strategist evals.

## M7 — Scout
Connector interface, first supported ATS connectors, ingestion, source health and deduplication.

## M8 — Orchestrated pipeline
Scheduler/queue, workflow state, AgentRun/WorkflowRun, thresholds and ranking.

## M9 — Basic UI
Profiler onboarding, profile preview, shortlist, job detail and feedback.

## M10 — Test/production deployment
GitHub Actions, managed environments, migrations, observability and release flow.

## M11 — Real-world evaluation
Run against live market, collect feedback, measure Precision@5/acceptance/unsupported claims and publish findings.
