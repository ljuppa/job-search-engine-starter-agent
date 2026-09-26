from datetime import UTC, datetime
from uuid import uuid4

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.domain.contracts import AgentRun, WorkflowRun
from src.persistence.models import Base
from src.persistence.orchestration_repository import OrchestrationRepository


def pending_workflow() -> WorkflowRun:
    return WorkflowRun(
        workflow_run_id=uuid4(),
        revision=1,
        workflow_name="job_discovery",
        correlation_id=uuid4(),
        trace_id=uuid4(),
        scope="GLOBAL",
        status="PENDING",
        input_reference="source-run:1",
        recorded_at=datetime.now(UTC),
    )


def revise(workflow_run: WorkflowRun, **updates: object) -> WorkflowRun:
    return WorkflowRun.model_validate({**workflow_run.model_dump(), **updates})


def test_workflow_revisions_are_append_only_and_transitioned_deterministically() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    repository = OrchestrationRepository(sessionmaker(bind=engine, expire_on_commit=False))
    pending = pending_workflow()

    repository.transition_workflow_run(pending)
    running = revise(
        pending,
        revision=2,
        status="RUNNING",
        started_at=datetime.now(UTC),
        recorded_at=datetime.now(UTC),
    )
    repository.transition_workflow_run(running)
    succeeded = revise(
        running,
        revision=3,
        status="SUCCEEDED",
        completed_at=datetime.now(UTC),
        recorded_at=datetime.now(UTC),
        output_reference="jobs:1",
    )
    repository.transition_workflow_run(succeeded)

    assert repository.get_latest_workflow_run(pending.workflow_run_id) == succeeded
    with pytest.raises(ValueError, match="invalid workflow status transition"):
        repository.transition_workflow_run(revise(succeeded, revision=4, status="RUNNING"))


def test_agent_runs_are_immutable() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    repository = OrchestrationRepository(sessionmaker(bind=engine, expire_on_commit=False))
    now = datetime.now(UTC)
    agent_run = AgentRun(
        agent_run_id=uuid4(),
        workflow_run_id=uuid4(),
        agent_name="scout",
        status="SUCCEEDED",
        model="deterministic",
        prompt_version="not-applicable",
        schema_version="1.0",
        input_reference="source:greenhouse",
        output_reference="jobs:1",
        latency_ms=3,
        started_at=now,
        completed_at=now,
    )

    repository.save_agent_run(agent_run)
    with pytest.raises(ValueError, match="immutable"):
        repository.save_agent_run(agent_run)
