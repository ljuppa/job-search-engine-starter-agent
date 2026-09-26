from uuid import uuid4

import pytest

from src.agents.matcher import MatcherDraft, MatcherInput, MatcherService, MatchSignal
from src.domain.contracts import (
    CandidateProfile,
    ExecutionContext,
    ExecutionScope,
    JobProfile,
    ProfileStatus,
)


class RecordingRepository:
    def __init__(self): self.assessments = []
    def save(self, assessment): self.assessments.append(assessment)


class FixedExtractor:
    async def extract(self, matcher_input):
        return MatcherDraft(strengths=[MatchSignal(category="capability", detail="Leadership experience matches", confidence=0.9)])


@pytest.mark.asyncio
async def test_matcher_persists_versioned_fit_assessment() -> None:
    user_id = uuid4()
    candidate = CandidateProfile(user_id=user_id, profile_id=uuid4(), revision=2, profile_status=ProfileStatus.CONFIRMED)
    job = JobProfile(job_profile_id=uuid4(), job_id=uuid4(), revision=3, analysed_at="2026-09-26T00:00:00Z")
    matcher_input = MatcherInput(context=ExecutionContext(correlation_id=uuid4(), trace_id=uuid4(), workflow_run_id=uuid4(), scope=ExecutionScope.USER, user_id=user_id, candidate_profile_id=candidate.profile_id, candidate_profile_revision=2), candidate_profile=candidate, job_profile=job, agent_run_id=uuid4(), prompt_version="matcher.v1")
    repository = RecordingRepository()

    assessment = await MatcherService(repository, FixedExtractor()).run(matcher_input)

    assert assessment.assessment_type.value == "FIT"
    assert assessment.score == 60
    assert repository.assessments == [assessment]
