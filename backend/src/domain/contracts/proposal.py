"""Contracts for auditable, non-mutating candidate-profile change proposals."""

from enum import Enum

from pydantic import Field, JsonValue, field_validator

from .common import (
    EvidenceReference,
    PositiveRevision,
    StableId,
    UserScopedContract,
    UtcTimestamp,
)
from .profile import ConfidenceScore, EvidenceSourceType


class ProposalOperation(str, Enum):
    """The JSON Patch-style operation the later policy may apply."""

    ADD = "ADD"
    REMOVE = "REMOVE"
    REPLACE = "REPLACE"


class ProposalStatus(str, Enum):
    """Lifecycle state of a profile-change proposal."""

    PENDING = "PENDING"
    AUTO_ACCEPTED = "AUTO_ACCEPTED"
    USER_ACCEPTED = "USER_ACCEPTED"
    REJECTED = "REJECTED"
    SUPERSEDED = "SUPERSEDED"


class ProfileChangeProposal(UserScopedContract):
    """Evidence-backed proposal that cannot itself alter a candidate profile."""

    proposal_id: StableId
    profile_id: StableId
    base_profile_revision: PositiveRevision
    operation: ProposalOperation
    field_path: str = Field(min_length=2)
    old_value: JsonValue | None = None
    new_value: JsonValue | None = None
    rationale: str = Field(min_length=1)
    evidence_references: list[EvidenceReference] = Field(min_length=1)
    source_type: EvidenceSourceType
    confidence: ConfidenceScore
    status: ProposalStatus = ProposalStatus.PENDING
    created_at: UtcTimestamp
    resolved_at: UtcTimestamp | None = None

    @field_validator("field_path")
    @classmethod
    def validate_field_path(cls, value: str) -> str:
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
