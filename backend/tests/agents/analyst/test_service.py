from datetime import UTC, datetime
from uuid import uuid4

import pytest

from src.agents.analyst import AnalystInput, AnalystResult, AnalystService, JobFact, JobProfileDraft
from src.domain.contracts import ExecutionContext, ExecutionScope, Job, RawJob


def raw_job() -> RawJob:
    return RawJob(raw_job_id=uuid4(), source_name="test", external_id="123", source_url="https://example.com/jobs/123", retrieved_at=datetime.now(UTC), title="Engineering Manager", company_name="Example", description="Lead a software team. Remote in Europe.", source_payload={}, content_hash="abc")


def input_for(raw: RawJob) -> AnalystInput:
    job = Job(job_id=uuid4(), canonical_key="example-engineering-manager", raw_job_ids=[raw.raw_job_id], created_at=datetime.now(UTC), updated_at=datetime.now(UTC))
    return AnalystInput(context=ExecutionContext(correlation_id=uuid4(), trace_id=uuid4(), workflow_run_id=uuid4(), scope=ExecutionScope.GLOBAL), raw_job=raw, job=job, prompt_version="analyst.extract.v1")


class RecordingRepository:
    def __init__(self) -> None:
        self.saved = []

    def next_job_profile_revision(self, job_id):
        return 1

    def save_job_profile(self, profile, *, raw_job_id):
        self.saved.append((profile, raw_job_id))


class FixedExtractor:
    async def extract(self, analyst_input):
        return AnalystResult(facts=[JobFact(field_path="/seniority", value="manager", confidence=0.9)], profile_draft=JobProfileDraft(role_family="Engineering", seniority="Manager", requirements=["Lead a software team"], work_model="REMOTE", location="Europe"))


@pytest.mark.asyncio
async def test_analyst_creates_a_versioned_global_job_profile() -> None:
    raw = raw_job()
    repository = RecordingRepository()

    profile = await AnalystService(repository, FixedExtractor()).run(input_for(raw))

    assert profile.revision == 1
    assert profile.role_family == "Engineering"
    assert repository.saved[0][1] == raw.raw_job_id


def test_analyst_input_rejects_user_scope() -> None:
    raw = raw_job()
    with pytest.raises(ValueError, match="GLOBAL"):
        AnalystInput(context=ExecutionContext(correlation_id=uuid4(), trace_id=uuid4(), workflow_run_id=uuid4(), scope=ExecutionScope.USER, user_id=uuid4()), raw_job=raw, job=Job(job_id=uuid4(), canonical_key="job", raw_job_ids=[raw.raw_job_id], created_at=datetime.now(UTC), updated_at=datetime.now(UTC)), prompt_version="analyst.extract.v1")
