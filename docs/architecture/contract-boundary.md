# Domain Contract Boundary

The canonical domain-contract package is
`backend/src/domain/contracts/`. Production modules and evals import contracts
only through `src.domain.contracts`.

## Ownership and versioning

| Category | Contracts | Rule |
|---|---|---|
| Global job intelligence | `RawJob`, `Job`, `JobProfile` | No `user_id`. Jobs and source records can be reused across users. |
| User-owned records | `CandidateProfile`, `ProfileEvidence`, `ProfileChangeProposal`, `Assessment`, `Recommendation`, `UserFeedback` | `user_id` is required. |
| Execution attribution | `ExecutionContext` | Scope is explicit. `USER` requires `user_id`; `GLOBAL` forbids it. |

Revisions are positive integers scoped to their stable aggregate IDs. Assessments
and recommendations record the exact candidate-profile and job-profile revisions
used. A profile change is an evidence-backed proposal, never an implicit profile
mutation.

## Compatibility evidence

Each root contract has a synthetic versioned JSON example in `data/schemas/`.
The contract suite validates every example and generates JSON Schema directly
from the Pydantic models. There are no hand-maintained duplicate schemas.

## M1 scope review

M1 introduces contracts, fixtures and tests only. It deliberately contains no
persistence, provider implementation, workflow orchestration, agent behaviour,
ranking policy or connector logic. No approved deviations are recorded.
