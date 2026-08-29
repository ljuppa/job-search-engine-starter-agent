# Personal Job Search Engine — v0.1

A profile-driven job intelligence system that continuously discovers roles, normalizes them, evaluates **current fit** and **career value**, ranks them, and learns from explicit user feedback.

## Product thesis

Normal job platforms optimize for volume. This product optimizes for **signal**: from hundreds of jobs, surface a small number of opportunities the user would genuinely consider.

The distinguishing model is:

- **Matcher:** Can this person realistically do the job?
- **Strategist:** Is this job a good next career move?

## v0.1 architecture

Five reasoning agents:

1. **Profiler** — builds and maintains the canonical candidate profile.
2. **Scout** — discovers jobs from configured sources.
3. **Analyst** — converts raw job postings into normalized `JobProfile` objects.
4. **Matcher** — assesses present-day candidate/job fit.
5. **Strategist** — assesses long-term career value.

Deterministic services own hard constraints, ranking, deduplication, workflow state and persistence.

## Technology baseline

- Python + FastAPI
- Pydantic
- PostgreSQL
- SQLAlchemy + Alembic
- PostgreSQL-backed async queue initially
- Next.js + React + TypeScript
- Provider-neutral LLM Gateway; OpenAI adapter first
- HTTPX / BeautifulSoup / Playwright for connectors
- pytest + custom eval runner
- OpenTelemetry
- Docker + Docker Compose
- GitHub Actions

## Getting started

```bash
cp .env.example .env
make setup
make dev
```

Then open the repository in VS Code with the Codex extension enabled.

## How to work with Codex

Read `AGENTS.md` first. Every meaningful change should start from an issue and follow:

`requirement → design → human approval → implementation → tests/evals → review → human understanding → merge`

## Documentation

- `docs/product/product-charter.md`
- `docs/architecture/software-design-charter.md`
- `docs/architecture/data-model.md`
- `docs/architecture/infrastructure.md`
- `docs/architecture/scaling.md`
- `docs/evals/evals-architecture.md`
- `docs/ux/ux-strategy.md`
- `docs/way-of-working/ai-assisted-development.md`
- `docs/adr/`

## Milestones

See `docs/roadmap/milestones.md`.
