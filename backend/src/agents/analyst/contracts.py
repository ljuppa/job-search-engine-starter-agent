"""Typed boundary contracts for global Analyst executions."""

from typing import Annotated

from pydantic import Field, model_validator

from src.domain.contracts import (
    ConfidenceScore,
    ContractModel,
    ExecutionContext,
    ExecutionScope,
    Job,
    JobCompensation,
    RawJob,
    WorkModel,
)

type NonEmptyText = Annotated[str, Field(min_length=1)]


class JobFact(ContractModel):
    """One source-grounded claim extracted from a frozen raw job."""

    field_path: NonEmptyText
    value: object | None = None
    confidence: ConfidenceScore

    @model_validator(mode="after")
    def validate_path(self) -> "JobFact":
        if not self.field_path.startswith("/") or self.field_path == "/":
            raise ValueError("field_path must be a non-root JSON Pointer")
        return self


class JobProfileDraft(ContractModel):
    """LLM-derived analysis without IDs, revisions, or timestamps."""

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


class AnalystInput(ContractModel):
    context: ExecutionContext
    raw_job: RawJob
    job: Job
    prompt_version: NonEmptyText

    @model_validator(mode="after")
    def validate_global_scope_and_job_link(self) -> "AnalystInput":
        if self.context.scope is not ExecutionScope.GLOBAL:
            raise ValueError("AnalystInput requires a GLOBAL execution context")
        if self.raw_job.raw_job_id not in self.job.raw_job_ids:
            raise ValueError("canonical Job must reference the supplied RawJob")
        return self


class AnalystResult(ContractModel):
    facts: list[JobFact] = Field(default_factory=list)
    profile_draft: JobProfileDraft
