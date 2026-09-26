"""Versioned, auditable contracts for explicit workflow orchestration."""

from enum import Enum
from typing import Annotated

from pydantic import Field, model_validator

from .common import ContractModel, StableId, UtcTimestamp, VersionedContract
from .execution import ExecutionScope

type NonEmptyText = Annotated[str, Field(min_length=1)]
type NonNegativeMilliseconds = Annotated[int, Field(ge=0)]
type NonNegativeTokens = Annotated[int, Field(ge=0)]


class RunStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class QueueStatus(str, Enum):
    READY = "READY"
    RUNNING = "RUNNING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"


class Usage(ContractModel):
    """Provider-neutral token accounting captured for one agent execution."""

    input_tokens: NonNegativeTokens = 0
    output_tokens: NonNegativeTokens = 0


class WorkflowRun(VersionedContract):
    """One immutable state revision of an explicitly orchestrated workflow."""

    workflow_run_id: StableId
    workflow_name: NonEmptyText
    correlation_id: StableId
    trace_id: StableId
    scope: ExecutionScope
    user_id: StableId | None = None
    status: RunStatus
    input_reference: NonEmptyText
    output_reference: NonEmptyText | None = None
    error_code: NonEmptyText | None = None
    started_at: UtcTimestamp | None = None
    completed_at: UtcTimestamp | None = None
    recorded_at: UtcTimestamp

    @model_validator(mode="after")
    def validate_lifecycle_and_scope(self) -> "WorkflowRun":
        if (self.scope is ExecutionScope.USER) != (self.user_id is not None):
            raise ValueError("user_id is required for USER scope and forbidden for GLOBAL scope")
        if self.status is RunStatus.PENDING and self.started_at is not None:
            raise ValueError("pending workflows must not have started")
        if self.status is RunStatus.RUNNING and self.started_at is None:
            raise ValueError("running workflows require started_at")
        if self.status in {RunStatus.SUCCEEDED, RunStatus.FAILED, RunStatus.CANCELLED} and (
            self.started_at is None or self.completed_at is None
        ):
            raise ValueError("terminal workflows require started_at and completed_at")
        if self.status is RunStatus.SUCCEEDED and self.output_reference is None:
            raise ValueError("successful workflows require output_reference")
        if self.status is RunStatus.FAILED and self.error_code is None:
            raise ValueError("failed workflows require error_code")
        return self


class AgentRun(ContractModel):
    """Immutable audit record for one completed logical-agent execution."""

    agent_run_id: StableId
    workflow_run_id: StableId
    agent_name: NonEmptyText
    status: RunStatus
    model: NonEmptyText
    prompt_version: NonEmptyText
    input_reference: NonEmptyText
    output_reference: NonEmptyText | None = None
    schema_version: NonEmptyText
    latency_ms: NonNegativeMilliseconds
    usage: Usage = Field(default_factory=Usage)
    error_code: NonEmptyText | None = None
    started_at: UtcTimestamp
    completed_at: UtcTimestamp

    @model_validator(mode="after")
    def validate_terminal_result(self) -> "AgentRun":
        if self.status not in {RunStatus.SUCCEEDED, RunStatus.FAILED, RunStatus.CANCELLED}:
            raise ValueError("agent runs must record a terminal status")
        if self.status is RunStatus.SUCCEEDED and self.output_reference is None:
            raise ValueError("successful agent runs require output_reference")
        if self.status is RunStatus.FAILED and self.error_code is None:
            raise ValueError("failed agent runs require error_code")
        return self


class WorkflowTask(ContractModel):
    """Durable PostgreSQL-backed work item; retries are deterministic code."""

    task_id: StableId
    workflow_run_id: StableId
    workflow_name: NonEmptyText
    payload: dict[str, object]
    status: QueueStatus = QueueStatus.READY
    attempt_count: Annotated[int, Field(ge=0)] = 0
    max_attempts: Annotated[int, Field(ge=1)] = 3
    available_at: UtcTimestamp
    error_code: NonEmptyText | None = None
