"""Deterministic creation of user-scoped CAREER assessments."""

from datetime import UTC, datetime
from typing import Protocol
from uuid import uuid4

from src.domain.contracts import Assessment, AssessmentType
from src.persistence.assessment_repository import AssessmentRepository

from .contracts import StrategistDraft, StrategistInput
from .policy import calculate_career_score


class StrategistExtractor(Protocol):
    async def extract(self, strategist_input: StrategistInput) -> StrategistDraft: ...


class StrategistService:
    def __init__(self, repository: AssessmentRepository, extractor: StrategistExtractor) -> None:
        self._repository = repository
        self._extractor = extractor

    async def run(self, strategist_input: StrategistInput) -> Assessment:
        draft = await self._extractor.extract(strategist_input)
        assessment = Assessment(assessment_id=uuid4(), assessment_type=AssessmentType.CAREER, user_id=strategist_input.candidate_profile.user_id, job_id=strategist_input.job_profile.job_id, candidate_profile_id=strategist_input.candidate_profile.profile_id, candidate_profile_revision=strategist_input.candidate_profile.revision, job_profile_id=strategist_input.job_profile.job_profile_id, job_profile_revision=strategist_input.job_profile.revision, score=calculate_career_score(draft), confidence=min([signal.confidence for signal in draft.opportunities + draft.risks + draft.uncertainties] or [0.5]), strengths=[signal.detail for signal in draft.opportunities], gaps=[], risks=[signal.detail for signal in draft.risks + draft.uncertainties], agent_run_id=strategist_input.agent_run_id, assessed_at=datetime.now(UTC))
        self._repository.save(assessment)
        return assessment
