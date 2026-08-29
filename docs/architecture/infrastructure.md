# Infrastructure and Deployment — v0.1

## Environments

### Local
Docker Compose on developer Mac. Host-native VS Code, Git, Codex and Docker Desktop; application runtime in containers. Local PostgreSQL data is disposable and is not synchronized between computers.

### Test
Structurally similar to production, but fully isolated database, credentials, queues and LLM budget/project. Used for integration tests, agent evals, smoke tests and pre-release validation.

### Production
Frontend, API, worker, scheduler and managed PostgreSQL. Stateless workers scale horizontally. External dependencies include LLM providers and job sources.

## Deployment units

- Next.js frontend
- FastAPI API
- Python worker
- Python scheduler
- PostgreSQL

API and workers may share one backend Docker image with different commands.

## Technology

- Docker / Docker Compose
- GitHub Actions
- Managed PostgreSQL
- PostgreSQL-backed task queue initially
- S3-compatible object storage when uploads/artifacts are introduced
- OpenTelemetry for traces/metrics/log correlation
- Provider-neutral LLM Gateway

## CI/CD

PR: checkout → setup → lint/type/security → unit/integration/contract tests → eval subset → build.

Main: full tests/evals → immutable Docker images → deploy Test → migrations → smoke/E2E → manual approval → promote same images to Production → post-deploy checks.

## Security baseline

HTTPS, encrypted DB/storage connections, secrets management, authentication/authorization before multi-user exposure, rate limiting, input validation, dependency scanning, audit trail.

## Reliability principle

For this product, retryability, idempotency and recoverability matter more than extreme uptime. A Scout run may be late; profile state must not be lost.
