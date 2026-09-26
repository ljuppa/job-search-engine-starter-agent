from datetime import UTC, datetime
from uuid import uuid4

import pytest
from pydantic import ValidationError

from src.domain.contracts import AgentRun, RunStatus, WorkflowRun


def workflow(**updates: object) -> WorkflowRun:
    payload: dict[str, object] = {
        "workflow_run_id": uuid4(),
        "revision": 1,
        "workflow_name": "job_discovery",
        "correlation_id": uuid4(),
        "trace_id": uuid4(),
        "scope": "GLOBAL",
        "status": "PENDING",
        "input_reference": "raw-source-run:123",
        "recorded_at": datetime.now(UTC),
    }
    payload.update(updates)
    return WorkflowRun.model_validate(payload)


def test_workflow_run_enforces_scope_and_lifecycle_boundaries() -> None:
    assert workflow().status is RunStatus.PENDING

    with pytest.raises(ValidationError, match="pending workflows"):
        workflow(started_at=datetime.now(UTC))
    with pytest.raises(ValidationError, match="USER scope"):
        workflow(scope="USER")
    with pytest.raises(ValidationError, match="output_reference"):
        workflow(
            status="SUCCEEDED",
            started_at=datetime.now(UTC),
            completed_at=datetime.now(UTC),
        )


def test_agent_run_requires_a_complete_audit_record() -> None:
    now = datetime.now(UTC)
    run = AgentRun(
        agent_run_id=uuid4(),
        workflow_run_id=uuid4(),
        agent_name="analyst",
        status="SUCCEEDED",
        model="gpt-test",
        prompt_version="analyst.v1",
        schema_version="1.0",
        input_reference="raw-job:123",
        output_reference="job-profile:456",
        latency_ms=24,
        usage={"input_tokens": 10, "output_tokens": 5},
        started_at=now,
        completed_at=now,
    )

    assert run.usage.output_tokens == 5
    with pytest.raises(ValidationError, match="terminal status"):
        AgentRun.model_validate({**run.model_dump(), "status": "RUNNING"})
