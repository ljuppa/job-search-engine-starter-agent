# Extensibility and Scaling — Single User to Multi User

## Core decision

Build v0.1 as single-user in behavior but multi-user-safe in ownership.

## Global/shared data

- Company
- JobSource
- RawJob
- Job
- JobProfile

A job is discovered and analyzed once, then reused for many users.

## User-specific data

- CandidateProfile
- SearchConfiguration
- FitAssessment
- CareerAssessment
- Recommendation
- UserFeedback
- Application state

## Rules

1. Private records carry `user_id` from day one.
2. Agents are stateless; state is loaded from persistence per execution.
3. Workflow context carries `correlation_id`, `user_id`, `workflow_run_id`, `profile_version`, `job_id`, `trace_id`.
4. Scout ingestion becomes global rather than repeated per user.
5. Analyst runs once per canonical job/profile version, not once per user.
6. Retrieval must become cheaper than LLM evaluation at scale.
7. Introduce tenant isolation/RLS before public multi-user launch.
8. Do not introduce `organization_id` until teams/recruiters/enterprise features actually exist.

## Scale stages

### Stage 0 — v0.1
1 user, 1 API, 1 worker, 1 scheduler, 1 PostgreSQL.

### Stage 1 — small beta
10–100 users: authentication, isolation, multiple workers, rate limits, queue priorities.

### Stage 2 — hundreds/low thousands
Global job ingestion, indexed candidate retrieval, async fan-out, caching, per-user cost controls, optional pgvector.

### Stage 3 — larger platform
Only then consider extracting Profile, Job Intelligence, Recommendation, Workflow and Notification services.

## LLM cost funnel

`100,000 active jobs → cheap structured/semantic retrieval → ~100/user → Matcher → ~20 → Strategist → ~5 surfaced`
