"""Typed boundary contracts for Profiler executions."""

from enum import Enum
from typing import Annotated
from uuid import UUID

from pydantic import Field, JsonValue, field_validator, model_validator

from src.domain.contracts import (
    CandidateProfile,
    ConfidenceScore,
    ContractModel,
    EvidenceSourceType,
    ExecutionContext,
    ExecutionScope,
    ProposalOperation,
)

type NonEmptyText = Annotated[str, Field(min_length=1)]


def _validate_non_root_json_pointer(value: str) -> str:
    if not value.startswith("/") or value == "/":
        raise ValueError("field_path must be a non-root JSON Pointer")

    for segment in value.split("/")[1:]:
        index = 0
        while index < len(segment):
            if segment[index] == "~":
                if index + 1 == len(segment) or segment[index + 1] not in {"0", "1"}:
                    raise ValueError("field_path contains an invalid JSON Pointer escape")
                index += 2
            else:
                index += 1
    return value


class FactDisposition(str, Enum):
    """Whether the source explicitly states a fact or the Profiler inferred it."""

    EXTRACTED = "EXTRACTED"
    INFERRED = "INFERRED"


class ProfilerSource(ContractModel):
    """A supplied source from which the Profiler may derive profile information."""

    source_id: UUID
    source_type: EvidenceSourceType
    source_reference: NonEmptyText
    content: NonEmptyText


class ProfilerInput(ContractModel):
    """The complete, user-scoped input to one Profiler execution."""

    context: ExecutionContext
    sources: list[ProfilerSource] = Field(min_length=1)
    current_profile: CandidateProfile | None = None
    prompt_version: NonEmptyText

    @model_validator(mode="after")
    def validate_user_scope_and_profile_reference(self) -> "ProfilerInput":
        if self.context.scope is not ExecutionScope.USER:
            raise ValueError("ProfilerInput requires a USER execution context")

        profile_reference = (
            self.context.candidate_profile_id,
            self.context.candidate_profile_revision,
        )
        if self.current_profile is None:
            if profile_reference != (None, None):
                raise ValueError("current_profile is required when context references a profile")
            return self

        if self.current_profile.user_id != self.context.user_id:
            raise ValueError("current_profile user_id must match the execution context")
        if profile_reference != (self.current_profile.profile_id, self.current_profile.revision):
            raise ValueError("context must reference the exact current_profile revision")
        return self


class ProfileFact(ContractModel):
    """One fact or inference extracted from supplied source material."""

    field_path: NonEmptyText
    value: JsonValue
    disposition: FactDisposition
    confidence: ConfidenceScore
    source_ids: list[UUID] = Field(min_length=1)

    @field_validator("field_path")
    @classmethod
    def validate_field_path(cls, value: str) -> str:
        return _validate_non_root_json_pointer(value)


class ProfileChangeDraft(ContractModel):
    """A non-persistent change candidate to be converted to a pending proposal."""

    operation: ProposalOperation
    field_path: NonEmptyText
    new_value: JsonValue | None = None
    rationale: NonEmptyText
    confidence: ConfidenceScore
    source_ids: list[UUID] = Field(min_length=1)

    @field_validator("field_path")
    @classmethod
    def validate_field_path(cls, value: str) -> str:
        return _validate_non_root_json_pointer(value)


class ProfilerQuestionTopic(str, Enum):
    SEARCH_POSTURE = "SEARCH_POSTURE"
    TARGET_ROLES = "TARGET_ROLES"
    ACCEPTABLE_ROLES = "ACCEPTABLE_ROLES"
    EXCLUDED_ROLES = "EXCLUDED_ROLES"
    PREFERRED_LOCATIONS = "PREFERRED_LOCATIONS"
    RELOCATION_ALLOWED = "RELOCATION_ALLOWED"
    WORK_MODEL = "WORK_MODEL"
    COMPENSATION = "COMPENSATION"
    CAREER_GOALS = "CAREER_GOALS"


class ProfilerQuestionKind(str, Enum):
    FREE_TEXT = "FREE_TEXT"
    SINGLE_SELECT = "SINGLE_SELECT"
    MULTI_SELECT = "MULTI_SELECT"
    BOOLEAN = "BOOLEAN"
    AMOUNT = "AMOUNT"


class ProfilerQuestionOption(ContractModel):
    key: NonEmptyText
    label: NonEmptyText


class ProfilerQuestion(ContractModel):
    """A question that requires explicit candidate input before confirmation."""

    topic: ProfilerQuestionTopic
    kind: ProfilerQuestionKind
    text: NonEmptyText
    required_for_confirmation: bool
    options: list[ProfilerQuestionOption] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_option_keys_are_unique(self) -> "ProfilerQuestion":
        option_keys = [option.key for option in self.options]
        if len(option_keys) != len(set(option_keys)):
            raise ValueError("question option keys must be unique")
        return self


class ProfilerResult(ContractModel):
    """Structured Profiler output; it cannot directly mutate a profile."""

    facts: list[ProfileFact] = Field(default_factory=list)
    change_drafts: list[ProfileChangeDraft] = Field(default_factory=list)
    questions: list[ProfilerQuestion] = Field(default_factory=list)
