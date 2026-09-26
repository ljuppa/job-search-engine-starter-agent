# M7 Backlog — Scout

## Milestone outcome

Global Greenhouse ingestion produces immutable RawJob records, deterministic
canonical jobs, and source-health observations without source logic leaking
into Scout orchestration.

### M7-01 — Greenhouse connector boundary

**Status:** Done

Parse frozen Greenhouse public-board payloads through a typed connector.

### M7-02 — Ingestion, deduplication, and source health

**Status:** Done

### M7-03 — Persistence, evals, and milestone review

**Status:** Done

## Delivered behaviour

- Exact source replays are idempotent by `(source_name, external_id, content_hash)`.
- Changed source content creates another immutable `RawJob` revision and links it
  to its existing canonical job.
- Cross-source equivalents are linked through the deterministic canonical key.
- Scout records one normalised source-health observation for each connector
  success or failure; raw exception text is never persisted as an error code.
- Frozen Greenhouse payloads, connector/ingestion/deduplication/source-health
  tests, and Scout eval discovery are included in this milestone.
