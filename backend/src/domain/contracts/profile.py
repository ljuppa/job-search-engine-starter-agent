"""Candidate-profile and profile-evidence contracts."""

from enum import Enum
from typing import Annotated

from pydantic import Field, model_validator

from .common import (
    ContractModel,
    EvidenceId,
    StableId,
    UserId,
    UserScopedVersionedContract,
    UtcTimestamp,
)

type ConfidenceScore = Annotated[float, Field(ge=0, le=1)]
type NonEmptyText = Annotated[str, Field(min_length=1)]
type CurrencyCode = Annotated[str, Field(pattern=r"^[A-Z]{3}$")]


class ProfileStatus(str, Enum):
    """Lifecycle state of the candidate profile."""

    DRAFT = "DRAFT"
    CONFIRMED = "CONFIRMED"
    ARCHIVED = "ARCHIVED"


class SearchPosture(str, Enum):
    """How actively the candidate is pursuing a change."""

    ACTIVE = "ACTIVE"
    SELECTIVE = "SELECTIVE"
    EXPLORATORY = "EXPLORATORY"


class EvidenceSourceType(str, Enum):
    """Origin of a claim used in the candidate profile."""

    USER_STATED = "USER_STATED"
    CV = "CV"
    INFERRED = "INFERRED"
    FEEDBACK = "FEEDBACK"
    SYSTEM = "SYSTEM"


class WorkModel(str, Enum):
    REMOTE = "REMOTE"
    HYBRID = "HYBRID"
    ONSITE = "ONSITE"


class LocationPreferences(ContractModel):
    preferred_locations: list[NonEmptyText] = Field(default_factory=list)
    relocation_allowed: bool | None = None


class CompensationPreferences(ContractModel):
    currency: CurrencyCode | None = None
    minimum_annual_amount: int | None = Field(default=None, ge=0)
    target_annual_amount: int | None = Field(default=None, ge=0)

    @model_validator(mode="after")
    def validate_amounts(self) -> "CompensationPreferences":
        amounts = (self.minimum_annual_amount, self.target_annual_amount)
        if any(amount is not None for amount in amounts) and self.currency is None:
            raise ValueError("currency is required when compensation amounts are set")
        if (
            self.minimum_annual_amount is not None
            and self.target_annual_amount is not None
            and self.minimum_annual_amount > self.target_annual_amount
        ):
            raise ValueError("minimum_annual_amount cannot exceed target_annual_amount")
        return self


class WorkModelPreferences(ContractModel):
    acceptable_models: list[WorkModel] = Field(default_factory=list)


class ProfileEvidence(ContractModel):
    """Canonical, user-owned evidence supporting a profile claim."""

    evidence_id: EvidenceId
    user_id: UserId
    source_type: EvidenceSourceType
    source_reference: NonEmptyText
    captured_claim: NonEmptyText
    confidence: ConfidenceScore
    captured_at: UtcTimestamp


class CandidateProfile(UserScopedVersionedContract):
    """Canonical, versioned representation of a candidate's declared profile."""

    profile_id: StableId
    profile_status: ProfileStatus
    search_posture: SearchPosture | None = None
    summary: NonEmptyText | None = None
    career_history: list[NonEmptyText] = Field(default_factory=list)
    capabilities: list[NonEmptyText] = Field(default_factory=list)
    achievements: list[NonEmptyText] = Field(default_factory=list)
    target_roles: list[NonEmptyText] = Field(default_factory=list)
    acceptable_roles: list[NonEmptyText] = Field(default_factory=list)
    excluded_roles: list[NonEmptyText] = Field(default_factory=list)
    hard_constraints: list[NonEmptyText] = Field(default_factory=list)
    soft_preferences: list[NonEmptyText] = Field(default_factory=list)
    career_goals: list[NonEmptyText] = Field(default_factory=list)
    strengths: list[NonEmptyText] = Field(default_factory=list)
    gaps: list[NonEmptyText] = Field(default_factory=list)
    location_preferences: LocationPreferences = Field(default_factory=LocationPreferences)
    compensation_preferences: CompensationPreferences = Field(
        default_factory=CompensationPreferences
    )
    work_model_preferences: WorkModelPreferences = Field(default_factory=WorkModelPreferences)
    confidence_map: dict[NonEmptyText, ConfidenceScore] = Field(default_factory=dict)
