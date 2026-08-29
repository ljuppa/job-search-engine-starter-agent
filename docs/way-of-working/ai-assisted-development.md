# AI-Assisted Development Way of Working

## Objective

Build a working product while deliberately developing hands-on engineering knowledge and creating a credible portfolio repository.

The human developer is Product Owner, Architect, Tech Lead and merge authority. Codex is an implementation/review/teaching partner.

## Development loop

`requirement → GitHub issue → design discussion → human approval → Codex implementation → tests/evals → Codex review → human understanding → PR approval → CI/CD`

## Two-computer model

GitHub is the source of truth. Both MacBook and Mac mini use the same VS Code + Codex + Docker workflow. Never synchronize source directories or local PostgreSQL through iCloud/Dropbox.

Finish on one Mac:

```bash
make test
git status
git add .
git commit
git push
```

Start on the other:

```bash
git pull
make dev
make migrate
```

## AI interaction modes

### Architect
Ask Codex to inspect the issue/architecture and propose interfaces/affected modules before coding.

### Implementer
After approval, implement only agreed scope and tests.

### Teacher
Explain implementation choices and concepts until the human can explain them independently.

### Reviewer
Use a fresh review context to look for correctness, architecture violations, missing tests and unnecessary complexity.

## Git workflow

- protect `main`
- feature branches such as `feat/candidate-profile`
- PR for every meaningful feature, even as solo developer
- CI/eval gates before merge
- no direct commits to `main`

## Learning journal

Maintain short notes in `learning/`: what was learned, what was implemented, important trade-offs and remaining questions.

## Portfolio evidence

Keep product charter, UX strategy, ADRs, data model, agent/eval architecture, CI/CD, implementation, deployment and measured eval results in the repository.
