from uuid import uuid4

import pytest

from src.agents.strategist import (
    StrategicSignal,
    StrategistDraft,
    StrategistInput,
    StrategistService,
)
from src.domain.contracts import (
    CandidateProfile,
    ExecutionContext,
    ExecutionScope,
    JobProfile,
    ProfileStatus,
)


class Repository:
    def __init__(self): self.saved = []
    def save(self, assessment): self.saved.append(assessment)


class Extractor:
    async def extract(self, strategist_input):
        return StrategistDraft(opportunities=[StrategicSignal(category="scope", detail="Broader leadership scope", confidence=0.8)], risks=[StrategicSignal(category="goal", detail="Industry alignment is uncertain", confidence=0.6)])


@pytest.mark.asyncio
async def test_strategist_creates_independent_career_assessment() -> None:
    user_id = uuid4()
    profile = CandidateProfile(user_id=user_id, profile_id=uuid4(), revision=1, profile_status=ProfileStatus.CONFIRMED, career_goals=["Lead larger teams"])
    job = JobProfile(job_profile_id=uuid4(), job_id=uuid4(), revision=1, analysed_at="2026-09-26T00:00:00Z", leadership_scope="Leads managers")
    input_ = StrategistInput(context=ExecutionContext(correlation_id=uuid4(), trace_id=uuid4(), workflow_run_id=uuid4(), scope=ExecutionScope.USER, user_id=user_id, candidate_profile_id=profile.profile_id, candidate_profile_revision=1), candidate_profile=profile, job_profile=job, agent_run_id=uuid4(), prompt_version="strategist.v1")
    repository = Repository()

    assessment = await StrategistService(repository, Extractor()).run(input_)

    assert assessment.assessment_type.value == "CAREER"
    assert assessment.score == 48
    assert repository.saved == [assessment]
