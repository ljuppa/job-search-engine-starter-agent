# User Experience Strategy — v0.1

## UX charter

The product should feel like a career advisor with a strong search engine behind it, not another job board. Optimize for low cognitive load, high trust, few high-quality decisions, progressive profiling and strong user control.

## Personas

### Active Senior Job Seeker
Actively looking, clearer targets, frequent review. Needs recall, fit analysis and faster discovery.

### Selective Career Mover — primary v0.1 persona
Currently employed and moves only for a meaningful opportunity. Needs low noise, career-value analysis and passive monitoring.

### Career Explorer
Considering a pivot with several plausible directions. Needs deeper profiling, exploratory recommendations and gap discovery.

Profiler derives search posture: `ACTIVE`, `SELECTIVE`, `EXPLORATORY`.

## Core surfaces

1. Onboarding
2. Profile
3. Shortlist
4. Job detail
5. Feedback
6. Search settings

## Primary flow

`Sign in → Profiler onboarding → profile preview → confirm/edit → search starts → background pipeline → shortlist → interested/maybe/ignore → reason → Profiler learning → improved future results`

## Onboarding

Use CV/profile ingestion + adaptive conversation + structured confirmation. Hard constraints require direct confirmation. Before activation show: **What I know / What I inferred / What I'm unsure about**.

## Shortlist card

Answer four questions quickly: What is it? Why does it fit? Why is it strategically interesting? What is the biggest concern?

Expose Fit and Career scores separately.

## Feedback

One-click: `Interested`, `Maybe`, `Ignore`; optional reason. `Never show roles like this` should trigger profile review rather than silent hard-filter creation.

## Trust

Show confidence and provenance. Avoid pretending scores are objective truth. Provide layered explainability from card summary to requirement/profile evidence.

## UX tests

- usability: onboarding, correction, shortlist selection, constraint edit
- trust: understanding explanations, fact/inference distinction, willingness to act
- recommendation quality: compare human labels with system ranking

Core edge cases: preference vs hard constraint, unsupported leader-of-leaders inference, great fit/bad career move, hard salary violation, repeated negative feedback.
