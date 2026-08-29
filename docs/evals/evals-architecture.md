# Evals Architecture — v0.1

## Goal

Determine whether each agent produces outputs accurate, useful, stable and safe enough for downstream stages.

## Four layers

1. Unit evals — one agent on one task.
2. Contract evals — schemas/rules/provenance.
3. Pipeline evals — multiple-agent/end-to-end behavior.
4. Product evals — whether users actually value recommendations.

## Core objects

- EvalDataset
- EvalCase
- EvalRun
- EvalResult
- EvalMetric

## Agent focus

### Profiler
Fact extraction, constraint recall, correct source attribution, inference discipline, safe profile updates.

### Scout
Recall, precision, duplicate rate, freshness and source reliability.

### Analyst
Field accuracy/recall, classification, unsupported inference, unknown-field detection.

### Matcher
Human-band agreement, gap/strength detection, hard-constraint compliance and unsupported-claim rate.

### Strategist
Declared-goal alignment, risk identification, consistency and unsupported claims.

### Ranker
Formula correctness, hard-filter correctness, ordering stability, tie breaking.

## Product metrics

Primary v0.1 metrics:

- `Precision@5`
- Unsupported Claim Rate
- User Acceptance Rate

Supporting metrics include NDCG@5, Strong Match acceptance, application conversion and false-positive reason distribution.

## Datasets

- synthetic edge-case set
- frozen real-world job set
- user-labeled set grown from actual feedback

## Evaluation hierarchy

Deterministic checks → human-labeled gold set → LLM judge where useful → live user feedback.

## Regression rule

Every meaningful prompt/model/agent change runs against versioned frozen eval sets and records agent version, prompt version, model, schema, cost and latency.
