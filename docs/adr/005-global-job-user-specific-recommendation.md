# ADR-005 — Global Job Intelligence, User-Specific Recommendation

**Status:** Accepted

## Decision
RawJob, canonical Job and JobProfile are globally reusable. CandidateProfile, FitAssessment, CareerAssessment, Recommendation and Feedback are user-scoped.

## Consequences
A job is ingested/analyzed once and evaluated separately for each user, giving a clean path to multi-user scale and lower LLM cost.
