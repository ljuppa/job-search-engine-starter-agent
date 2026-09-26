"""Typed boundaries for user-scoped Matcher executions."""

from typing import Annotated
from uuid import UUID

from pydantic import Field, model_validator

from src.domain.contracts import (
    CandidateProfile,
    ContractModel,
    ExecutionContext,
    ExecutionScope,
    JobProfile,
)
from src.domain.contracts.profile import ConfidenceScore

type NonEmptyText = Annotated[str, Field(min_length=1)]


class MatchSignal(ContractModel):
    category: NonEmptyText
    detail: NonEmptyText
    confidence: ConfidenceScore
    profile_field: NonEmptyText | None = None
    job_field: NonEmptyText | None = None


class MatcherDraft(ContractModel):
    strengths: list[MatchSignal] = Field(default_factory=list)
    gaps: list[MatchSignal] = Field(default_factory=list)
    risks: list[MatchSignal] = Field(default_factory=list)


class MatcherInput(ContractModel):
    context: ExecutionContext
    candidate_profile: CandidateProfile
    job_profile: JobProfile
    agent_run_id: UUID
    prompt_version: NonEmptyText

    @model_validator(mode="after")
    def validate_versions_and_scope(self) -> "MatcherInput":
        if self.context.scope is not ExecutionScope.USER:
            raise ValueError("MatcherInput requires a USER execution context")
        if self.context.user_id != self.candidate_profile.user_id:
            raise ValueError("candidate profile must belong to the execution user")
        if (self.context.candidate_profile_id, self.context.candidate_profile_revision) != (self.candidate_profile.profile_id, self.candidate_profile.revision):
            raise ValueError("context must reference the exact candidate profile revision")
        return self
