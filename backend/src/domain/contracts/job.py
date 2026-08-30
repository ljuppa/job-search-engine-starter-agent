"""Global job-intelligence contracts.

Raw source records, canonical jobs and Analyst-derived job profiles are shared
across users. They deliberately carry no user ownership field.
"""

from typing import Annotated

from pydantic import Field, HttpUrl, JsonValue, field_validator, model_validator

from .common import ContractModel, StableId, UtcTimestamp, VersionedContract
from .profile import ConfidenceScore, CurrencyCode, WorkModel

type NonEmptyText = Annotated[str, Field(min_length=1)]
type ContentHash = Annotated[str, Field(min_length=1)]


class RawJob(ContractModel):
    """Immutable capture of one external job-posting source record."""

    raw_job_id: StableId
    source_name: NonEmptyText
    external_id: NonEmptyText
    source_url: HttpUrl
    retrieved_at: UtcTimestamp
    published_at: UtcTimestamp | None = None
    updated_at: UtcTimestamp | None = None
    title: NonEmptyText
    company_name: NonEmptyText
    location: NonEmptyText | None = None
    description: NonEmptyText
    source_payload: JsonValue
    content_hash: ContentHash


class Job(ContractModel):
    """Global, deduplicated identity that groups equivalent raw source records."""

    job_id: StableId
    canonical_key: NonEmptyText
    raw_job_ids: list[StableId] = Field(min_length=1)
    created_at: UtcTimestamp
    updated_at: UtcTimestamp

    @field_validator("raw_job_ids")
    @classmethod
    def validate_unique_raw_job_ids(cls, value: list[StableId]) -> list[StableId]:
        if len(value) != len(set(value)):
            raise ValueError("raw_job_ids must not contain duplicates")
        return value


class JobCompensation(ContractModel):
    """Compensation information stated or inferred for a job posting."""

    currency: CurrencyCode | None = None
    minimum_annual_amount: int | None = Field(default=None, ge=0)
    maximum_annual_amount: int | None = Field(default=None, ge=0)

    @model_validator(mode="after")
    def validate_amounts(self) -> "JobCompensation":
        amounts = (self.minimum_annual_amount, self.maximum_annual_amount)
        if any(amount is not None for amount in amounts) and self.currency is None:
            raise ValueError("currency is required when compensation amounts are set")
        if (
            self.minimum_annual_amount is not None
            and self.maximum_annual_amount is not None
            and self.minimum_annual_amount > self.maximum_annual_amount
        ):
            raise ValueError("minimum_annual_amount cannot exceed maximum_annual_amount")
        return self


class JobProfile(VersionedContract):
    """Versioned Analyst interpretation of a canonical job."""

    job_profile_id: StableId
    job_id: StableId
    analysed_at: UtcTimestamp
    role_family: NonEmptyText | None = None
    seniority: NonEmptyText | None = None
    leadership_scope: NonEmptyText | None = None
    leader_of_leaders: bool | None = None
    requirements: list[NonEmptyText] = Field(default_factory=list)
    responsibilities: list[NonEmptyText] = Field(default_factory=list)
    technical_expectations: list[NonEmptyText] = Field(default_factory=list)
    domains: list[NonEmptyText] = Field(default_factory=list)
    industry: NonEmptyText | None = None
    work_model: WorkModel | None = None
    location: NonEmptyText | None = None
    compensation: JobCompensation = Field(default_factory=JobCompensation)
    unknown_fields: list[NonEmptyText] = Field(default_factory=list)
    confidence_map: dict[NonEmptyText, ConfidenceScore] = Field(default_factory=dict)
