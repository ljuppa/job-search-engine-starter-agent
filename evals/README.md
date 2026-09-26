# Evals

Evals use production contracts while keeping expected behaviour versioned and deterministic.

## Profiler cases

`cases/profiler/` contains frozen synthetic cases. The M3 runner checks that
required facts are present, source IDs provide provenance, and forbidden
inferences are not returned. Gateway-backed extraction is exercised with fakes
in tests; live-provider evals are deliberately opt-in and require credentials.
