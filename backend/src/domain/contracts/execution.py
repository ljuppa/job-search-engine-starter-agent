"""Execution-context contract shared by agents, workflows and observability."""

from enum import Enum

from pydantic import model_validator

from .common import ContractModel, PositiveRevision, StableId, UserId


class ExecutionScope(str, Enum):
    """Whether an execution operates globally or for one user."""

    GLOBAL = "GLOBAL"
    USER = "USER"


class ExecutionContext(ContractModel):
    """Typed attribution context passed through an agent or workflow execution."""

    correlation_id: StableId
    trace_id: StableId
    workflow_run_id: StableId
    scope: ExecutionScope
    user_id: UserId | None = None
    candidate_profile_id: StableId | None = None
    candidate_profile_revision: PositiveRevision | None = None
    job_id: StableId | None = None

    @model_validator(mode="after")
    def validate_scope_and_profile_reference(self) -> "ExecutionContext":
        if self.scope is ExecutionScope.USER and self.user_id is None:
            raise ValueError("user_id is required for USER execution scope")
        if self.scope is ExecutionScope.GLOBAL and self.user_id is not None:
            raise ValueError("user_id is forbidden for GLOBAL execution scope")

        profile_reference = (self.candidate_profile_id, self.candidate_profile_revision)
        if (profile_reference[0] is None) != (profile_reference[1] is None):
            raise ValueError(
                "candidate_profile_id and candidate_profile_revision must be provided together"
            )
        return self
