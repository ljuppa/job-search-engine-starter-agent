"""Deterministic creation of user-scoped FIT assessments."""

from datetime import UTC, datetime
from typing import Protocol
from uuid import uuid4

from src.domain.contracts import Assessment, AssessmentType
from src.persistence.assessment_repository import AssessmentRepository

from .contracts import MatcherDraft, MatcherInput
from .policy import calculate_score, evaluate_constraints


class MatcherExtractor(Protocol):
    async def extract(self, matcher_input: MatcherInput) -> MatcherDraft: ...


class MatcherService:
    def __init__(self, repository: AssessmentRepository, extractor: MatcherExtractor) -> None:
        self._repository = repository
        self._extractor = extractor

    async def run(self, matcher_input: MatcherInput) -> Assessment:
        constraints = evaluate_constraints(matcher_input.candidate_profile, matcher_input.job_profile)
        draft = await self._extractor.extract(matcher_input)
        risks = [signal.detail for signal in draft.risks] + list(constraints.failures) + list(constraints.unknowns)
        assessment = Assessment(
            assessment_id=uuid4(), assessment_type=AssessmentType.FIT, user_id=matcher_input.candidate_profile.user_id,
            job_id=matcher_input.job_profile.job_id, candidate_profile_id=matcher_input.candidate_profile.profile_id,
            candidate_profile_revision=matcher_input.candidate_profile.revision,
            job_profile_id=matcher_input.job_profile.job_profile_id, job_profile_revision=matcher_input.job_profile.revision,
            score=calculate_score(constraints=constraints, strengths=len(draft.strengths), gaps=len(draft.gaps), risks=len(draft.risks)),
            confidence=min([signal.confidence for signal in draft.strengths + draft.gaps + draft.risks] or [0.5]),
            strengths=[signal.detail for signal in draft.strengths], gaps=[signal.detail for signal in draft.gaps], risks=risks,
            agent_run_id=matcher_input.agent_run_id, assessed_at=datetime.now(UTC),
        )
        self._repository.save(assessment)
        return assessment
