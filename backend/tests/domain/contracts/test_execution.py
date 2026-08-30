from uuid import uuid4

import pytest
from pydantic import ValidationError

from src.domain.contracts import ExecutionContext, ExecutionScope, RawJob


def valid_global_context_payload() -> dict[str, object]:
    return {
        "correlation_id": str(uuid4()),
        "trace_id": str(uuid4()),
        "workflow_run_id": str(uuid4()),
        "scope": "GLOBAL",
        "job_id": str(uuid4()),
    }


def valid_user_context_payload() -> dict[str, object]:
    return {
        "correlation_id": str(uuid4()),
        "trace_id": str(uuid4()),
        "workflow_run_id": str(uuid4()),
        "scope": "USER",
        "user_id": str(uuid4()),
        "candidate_profile_id": str(uuid4()),
        "candidate_profile_revision": 2,
        "job_id": str(uuid4()),
    }


def test_global_context_has_no_user_ownership() -> None:
    context = ExecutionContext.model_validate(valid_global_context_payload())

    assert context.scope is ExecutionScope.GLOBAL
    assert context.user_id is None


def test_user_context_round_trips_with_profile_and_job_references() -> None:
    context = ExecutionContext.model_validate(valid_user_context_payload())

    restored = ExecutionContext.model_validate_json(context.model_dump_json())

    assert restored.scope is ExecutionScope.USER
    assert restored.candidate_profile_revision == 2


@pytest.mark.parametrize(
    "payload",
    [
        {**valid_global_context_payload(), "user_id": str(uuid4())},
        {key: value for key, value in valid_user_context_payload().items() if key != "user_id"},
        {
            key: value
            for key, value in valid_user_context_payload().items()
            if key != "candidate_profile_revision"
        },
        {
            key: value
            for key, value in valid_user_context_payload().items()
            if key != "candidate_profile_id"
        },
    ],
)
def test_execution_context_rejects_invalid_scope_and_profile_references(
    payload: dict[str, object],
) -> None:
    with pytest.raises(ValidationError):
        ExecutionContext.model_validate(payload)


def test_public_contract_surface_supports_stable_imports() -> None:
    assert ExecutionContext.__module__ == "src.domain.contracts.execution"
    assert RawJob.__module__ == "src.domain.contracts.job"
