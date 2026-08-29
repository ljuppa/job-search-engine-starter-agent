# Product Charter — v0.1

## Problem

Job platforms optimize for volume and engagement rather than a professional's actual career direction. They generate noise, repeated postings and simplistic matching. They rarely distinguish between **a job the user can do** and **a job that advances the user's career**.

## Goal

Continuously identify high-value opportunities for a specific user and rank them using both present-day fit and long-term career value.

## Primary success statement

> From hundreds of available jobs, surface a small number of opportunities the user would genuinely consider applying for.

## Principles

- Profile-first
- Low noise
- Explainable recommendations
- Evidence-based reasoning
- Career-aware ranking
- Human-controlled decisions
- Adaptive through explicit feedback
- Modular agent responsibilities

## Major flow

`User → Profiler → CandidateProfile → Scout → RawJob → Analyst → JobProfile → Matcher + Strategist → deterministic Ranker → Shortlist → UserFeedback → Profiler`

## Five agents

### Profiler
Who is this person and what do they want? Builds and maintains the canonical candidate profile. Distinguishes facts, preferences and inferences.

### Scout
What relevant jobs exist? Discovers roles from configured sources and forwards plausible candidates without deep judgment.

### Analyst
What does this job actually require? Normalizes messy job descriptions into structured `JobProfile` data.

### Matcher
Can this user realistically do this job? Produces current-fit assessment using evidence from CandidateProfile and JobProfile.

### Strategist
Should this user want this job? Evaluates scope growth, market portability, career optionality, leadership development and alignment with long-term goals.

## Ranking

The Ranker is deterministic, not an agent. Initial conceptual weighting: Fit 50%, Career Value 40%, Opportunity Factors 10%. Hard constraints override scores.

## In scope

- conversational profiling
- structured candidate profile
- profile evidence/versioning
- selected job-source discovery
- deduplication
- normalized job understanding
- fit assessment
- career assessment
- deterministic ranking
- explainable shortlist
- explicit user feedback
- recurring background processing
- persistence and eval hooks

## Out of scope

- automatic applications
- automated recruiter messaging
- CV/cover-letter generation
- interview preparation/scheduling
- salary negotiation
- unrestricted LinkedIn scraping
- multi-user UI/platform administration
- billing
- advanced labor-market forecasting
- autonomous career decisions

## v0.1 product boundary

A single-user, profile-driven, continuously running job discovery and recommendation system using five specialized agents, deterministic ranking and an explicit feedback loop.
