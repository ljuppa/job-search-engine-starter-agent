# Evals

Evals use production contracts while keeping expected behaviour versioned and deterministic.

## Profiler cases

`cases/profiler/` contains frozen synthetic cases. The M3 runner checks that
required facts are present, source IDs provide provenance, and forbidden
inferences are not returned. Gateway-backed extraction is exercised with fakes
in tests; live-provider evals are deliberately opt-in and require credentials.

## Scout cases

`cases/scout/` contains frozen connector and ingestion expectations. They use the
versioned `frozen_jobs/greenhouse/` public-board payload, so M7 checks never call
an external job board. Run `python -m evals.runner` to validate case discovery.
