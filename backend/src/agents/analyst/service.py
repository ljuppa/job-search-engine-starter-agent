"""Deterministic construction and persistence of derived job profiles."""

from datetime import UTC, datetime
from typing import Protocol
from uuid import uuid4

from src.domain.contracts import JobProfile
from src.persistence.job_repository import JobRepository

from .contracts import AnalystInput, AnalystResult, JobProfileDraft


class AnalystExtractor(Protocol):
    async def extract(self, analyst_input: AnalystInput) -> AnalystResult: ...


class AnalystService:
    def __init__(self, repository: JobRepository, extractor: AnalystExtractor) -> None:
        self._repository = repository
        self._extractor = extractor

    async def run(self, analyst_input: AnalystInput) -> JobProfile:
        result = await self._extractor.extract(analyst_input)
        self._validate_facts(result, analyst_input)
        revision = self._repository.next_job_profile_revision(analyst_input.job.job_id)
        profile = JobProfile(
            job_profile_id=uuid4(), job_id=analyst_input.job.job_id, revision=revision,
            analysed_at=datetime.now(UTC), **result.profile_draft.model_dump(mode="python"),
        )
        self._repository.save_job_profile(profile, raw_job_id=analyst_input.raw_job.raw_job_id)
        return profile

    @staticmethod
    def _validate_facts(result: AnalystResult, analyst_input: AnalystInput) -> None:
        allowed_roots = set(JobProfileDraft.model_fields)
        for fact in result.facts:
            root = fact.field_path.split("/")[1]
            if root not in allowed_roots:
                raise ValueError("Analyst facts may not set system-managed JobProfile fields")
