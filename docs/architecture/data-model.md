# Data Model Architecture — v0.1

## Core aggregates

- User
- CandidateProfile
- SearchConfiguration
- Job
- Assessment
- Recommendation
- Feedback

## Ownership model

| Object | Scope | Canonical/Derived |
|---|---|---|
| User | User | Canonical |
| CandidateProfile | User | Canonical/versioned |
| ProfileEvidence | User | Canonical |
| ProfileChangeProposal | User | Derived proposal until committed |
| SearchConfiguration | User | Canonical |
| JobSource | Global | Canonical/configuration |
| RawJob | Global | Canonical/immutable source record |
| Job | Global | Canonical identity |
| JobProfile | Global | Derived/versioned |
| FitAssessment | User + Job | Derived |
| CareerAssessment | User + Job | Derived |
| Recommendation | User + Job | Derived |
| UserFeedback | User + Job | Canonical |
| AgentRun | User/global | Observability |
| WorkflowRun | User/global | Observability |
| Eval data | System | Evaluation |

## CandidateProfile

Contains career history, capabilities, achievements, leadership scope, industries, technologies, target/acceptable/excluded roles, hard constraints, soft preferences, career goals, strengths/gaps, location/compensation/work-model preferences, confidence map and version metadata.

## ProfileEvidence

Every important profile claim should be traceable to evidence with source type such as `USER_STATED`, `CV`, `INFERRED`, `FEEDBACK`, `SYSTEM`.

## ProfileChangeProposal

Profiler proposes updates with old/new values, reason, evidence, confidence, type and status (`PENDING`, `AUTO_ACCEPTED`, `USER_ACCEPTED`, `REJECTED`, `SUPERSEDED`).

## RawJob

Immutable representation of an external posting: source, external id, URL, timestamps, title/company/location/description, payload/content hash.

## Job

Canonical deduplicated identity shared across users. One Job may reference multiple RawJob source records.

## JobProfile

Analyst-derived structure: role family, seniority, leadership scope, leader-of-leaders flag, requirements, responsibilities, technical expectations, domain/industry, work model, location, compensation, unknown fields and confidence.

## Assessment

Shared assessment envelope with type `FIT` or `CAREER`, score, confidence, strengths, gaps/risks, evidence, profile/job versions and AgentRun reference.

## Recommendation

User-specific final output referencing job and assessments with final score, rank, classification, explanation and ranking version.

## UserFeedback

Actions: `INTERESTED`, `MAYBE`, `IGNORE`, `APPLIED`, `NOT_RELEVANT`, `NEVER_SHOW_SIMILAR` plus optional reason and free text.

## Versioning rule

Never rely on an unversioned singleton profile. Assessments reference the exact profile and job-profile versions used.
