"""Typed boundaries for user-scoped career-strategy assessment."""

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


class StrategicSignal(ContractModel):
    category: NonEmptyText
    detail: NonEmptyText
    confidence: ConfidenceScore


class StrategistDraft(ContractModel):
    opportunities: list[StrategicSignal] = Field(default_factory=list)
    risks: list[StrategicSignal] = Field(default_factory=list)
    uncertainties: list[StrategicSignal] = Field(default_factory=list)


class StrategistInput(ContractModel):
    context: ExecutionContext
    candidate_profile: CandidateProfile
    job_profile: JobProfile
    agent_run_id: UUID
    prompt_version: NonEmptyText

    @model_validator(mode="after")
    def validate_scope_and_revision(self) -> "StrategistInput":
        if self.context.scope is not ExecutionScope.USER or self.context.user_id != self.candidate_profile.user_id:
            raise ValueError("StrategistInput requires the profile owner's USER context")
        if (self.context.candidate_profile_id, self.context.candidate_profile_revision) != (self.candidate_profile.profile_id, self.candidate_profile.revision):
            raise ValueError("context must reference the exact candidate profile revision")
        return self
