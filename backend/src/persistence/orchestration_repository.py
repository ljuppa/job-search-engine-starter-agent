"""Persistence boundary for append-only workflow and agent execution audit records."""

from collections.abc import Callable
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.domain.contracts import AgentRun, RunStatus, WorkflowRun

from .models import AgentRunRecord, WorkflowRunRecord

_ALLOWED_TRANSITIONS = {
    RunStatus.PENDING: {RunStatus.RUNNING, RunStatus.CANCELLED},
    RunStatus.RUNNING: {RunStatus.SUCCEEDED, RunStatus.FAILED, RunStatus.CANCELLED},
}


class OrchestrationRepository:
    def __init__(self, session_factory: Callable[[], Session]) -> None:
        self._session_factory = session_factory

    def save_workflow_run(self, workflow_run: WorkflowRun) -> None:
        with self._session_factory() as session:
            if session.get(
                WorkflowRunRecord, (workflow_run.workflow_run_id, workflow_run.revision)
            ):
                raise ValueError("workflow run revisions are immutable")
            session.add(
                WorkflowRunRecord(
                    workflow_run_id=workflow_run.workflow_run_id,
                    revision=workflow_run.revision,
                    workflow_name=workflow_run.workflow_name,
                    correlation_id=workflow_run.correlation_id,
                    trace_id=workflow_run.trace_id,
                    scope=workflow_run.scope.value,
                    user_id=workflow_run.user_id,
                    status=workflow_run.status.value,
                    recorded_at=workflow_run.recorded_at,
                    snapshot=workflow_run.model_dump(mode="json"),
                )
            )
            session.commit()

    def get_latest_workflow_run(self, workflow_run_id: UUID) -> WorkflowRun | None:
        with self._session_factory() as session:
            record = session.scalar(
                select(WorkflowRunRecord)
                .where(WorkflowRunRecord.workflow_run_id == workflow_run_id)
                .order_by(WorkflowRunRecord.revision.desc())
                .limit(1)
            )
            return WorkflowRun.model_validate(record.snapshot) if record else None

    def transition_workflow_run(self, workflow_run: WorkflowRun) -> None:
        previous = self.get_latest_workflow_run(workflow_run.workflow_run_id)
        if previous is None:
            if workflow_run.revision != 1 or workflow_run.status is not RunStatus.PENDING:
                raise ValueError("a workflow must begin as pending revision 1")
        else:
            allowed = _ALLOWED_TRANSITIONS.get(previous.status, set())
            if workflow_run.revision != previous.revision + 1:
                raise ValueError("workflow revision must increment by one")
            if workflow_run.status not in allowed:
                raise ValueError("invalid workflow status transition")
            if (
                workflow_run.workflow_name,
                workflow_run.correlation_id,
                workflow_run.trace_id,
                workflow_run.scope,
                workflow_run.user_id,
                workflow_run.input_reference,
            ) != (
                previous.workflow_name,
                previous.correlation_id,
                previous.trace_id,
                previous.scope,
                previous.user_id,
                previous.input_reference,
            ):
                raise ValueError("workflow attribution and input reference are immutable")
        self.save_workflow_run(workflow_run)

    def save_agent_run(self, agent_run: AgentRun) -> None:
        with self._session_factory() as session:
            if session.get(AgentRunRecord, agent_run.agent_run_id):
                raise ValueError("agent runs are immutable")
            session.add(
                AgentRunRecord(
                    agent_run_id=agent_run.agent_run_id,
                    workflow_run_id=agent_run.workflow_run_id,
                    agent_name=agent_run.agent_name,
                    status=agent_run.status.value,
                    started_at=agent_run.started_at,
                    completed_at=agent_run.completed_at,
                    snapshot=agent_run.model_dump(mode="json"),
                )
            )
            session.commit()
