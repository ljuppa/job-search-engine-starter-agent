"""Shared primitives for the versioned domain-contract boundary."""

from datetime import UTC, datetime
from typing import Annotated, Final, Literal
from uuid import UUID

from pydantic import AfterValidator, BaseModel, ConfigDict, Field

CONTRACT_SCHEMA_VERSION: Final = "1.0"

type SchemaVersion = Literal["1.0"]
type StableId = UUID
type UserId = UUID
type EvidenceId = UUID
type PositiveRevision = Annotated[int, Field(ge=1)]


def _normalize_to_utc(value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("timestamp must include a UTC offset")
    return value.astimezone(UTC)


type UtcTimestamp = Annotated[datetime, AfterValidator(_normalize_to_utc)]


class ContractModel(BaseModel):
    """Base configuration and schema version for every public contract."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True, validate_assignment=True)

    schema_version: SchemaVersion = CONTRACT_SCHEMA_VERSION


class VersionedContract(ContractModel):
    """A contract representing one immutable revision of an aggregate."""

    revision: PositiveRevision


class UserScopedContract(ContractModel):
    """A private contract that belongs to exactly one user."""

    user_id: UserId


class UserScopedVersionedContract(VersionedContract):
    """A private, versioned contract such as a candidate profile."""

    user_id: UserId


class EvidenceReference(ContractModel):
    """Reference to evidence supporting a derived claim or decision."""

    evidence_id: EvidenceId
