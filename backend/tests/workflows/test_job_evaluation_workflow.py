from datetime import UTC, datetime
from uuid import uuid4

import pytest

from src.domain.contracts import (
    Assessment,
    AssessmentType,
    CandidateProfile,
    ExecutionContext,
    ExecutionScope,
    Job,
    JobProfile,
    ProfileStatus,
    RawJob,
)
from src.workflows.job_evaluation.service import JobEvaluationWorkflow


class Analyst:
    async def run(self, input_):
        return JobProfile(
            job_profile_id=uuid4(),
            job_id=input_.job.job_id,
            revision=1,
            analysed_at=datetime.now(UTC),
        )


class Assessor:
    async def run(self, input_):
        return Assessment(
            assessment_id=uuid4(),
            assessment_type=AssessmentType.FIT,
            user_id=input_.candidate_profile.user_id,
            job_id=input_.job_profile.job_id,
            candidate_profile_id=input_.candidate_profile.profile_id,
            candidate_profile_revision=input_.candidate_profile.revision,
            job_profile_id=input_.job_profile.job_profile_id,
            job_profile_revision=1,
            score=80,
            confidence=1,
            agent_run_id=input_.agent_run_id,
            assessed_at=datetime.now(UTC),
        )


@pytest.mark.asyncio
async def test_job_evaluation_workflow_coordinates_agents_without_agent_to_agent_calls() -> None:
    user_id, raw_id, job_id = uuid4(), uuid4(), uuid4()
    candidate = CandidateProfile(
        user_id=user_id, profile_id=uuid4(), revision=1, profile_status=ProfileStatus.CONFIRMED
    )
    context = ExecutionContext(
        correlation_id=uuid4(),
        trace_id=uuid4(),
        workflow_run_id=uuid4(),
        scope=ExecutionScope.USER,
        user_id=user_id,
        candidate_profile_id=candidate.profile_id,
        candidate_profile_revision=1,
        job_id=job_id,
    )
    raw = RawJob(
        raw_job_id=raw_id,
        source_name="test",
        external_id="1",
        source_url="https://example.com/1",
        retrieved_at=datetime.now(UTC),
        title="Engineer",
        company_name="Example",
        description="Build",
        source_payload={},
        content_hash="one",
    )
    job = Job(
        job_id=job_id,
        canonical_key="example:engineer:",
        raw_job_ids=[raw_id],
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )

    result = await JobEvaluationWorkflow(Analyst(), Assessor(), Assessor()).run(
        context=context, raw_job=raw, job=job, candidate_profile=candidate
    )

    assert result.job_profile.job_id == job_id
    assert result.fit_assessment.job_id == job_id
    assert result.career_assessment.job_id == job_id
