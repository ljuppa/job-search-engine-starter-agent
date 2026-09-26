from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.domain.contracts import Job, JobProfile, RawJob
from src.persistence.job_repository import JobRepository
from src.persistence.models import Base


def test_repository_persists_global_job_analysis_with_sequential_revisions() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    repository = JobRepository(sessionmaker(bind=engine, expire_on_commit=False))
    raw = RawJob(raw_job_id=uuid4(), source_name="test", external_id="1", source_url="https://example.com/jobs/1", retrieved_at=datetime.now(UTC), title="Engineer", company_name="Example", description="Build software", source_payload={}, content_hash="hash")
    job = Job(job_id=uuid4(), canonical_key="example-engineer", raw_job_ids=[raw.raw_job_id], created_at=datetime.now(UTC), updated_at=datetime.now(UTC))
    repository.save_raw_job(raw)
    repository.save_job(job)
    profile = JobProfile(job_profile_id=uuid4(), job_id=job.job_id, revision=repository.next_job_profile_revision(job.job_id), analysed_at=datetime.now(UTC), role_family="Engineering")

    repository.save_job_profile(profile, raw_job_id=raw.raw_job_id)

    assert profile.revision == 1
    assert repository.next_job_profile_revision(job.job_id) == 2


def test_raw_job_source_revisions_are_idempotent_by_source_identity_and_content() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    repository = JobRepository(sessionmaker(bind=engine, expire_on_commit=False))
    original = RawJob(
        raw_job_id=uuid4(), source_name="greenhouse", external_id="1",
        source_url="https://example.com/jobs/1", retrieved_at=datetime.now(UTC),
        title="Engineer", company_name="Example", description="Build software",
        source_payload={}, content_hash="hash-one",
    )
    replay = original.model_copy(update={"raw_job_id": uuid4()})
    changed = original.model_copy(update={"raw_job_id": uuid4(), "content_hash": "hash-two"})

    assert repository.save_raw_job(original).raw_job_id == original.raw_job_id
    assert repository.save_raw_job(replay).raw_job_id == original.raw_job_id
    assert repository.save_raw_job(changed).raw_job_id == changed.raw_job_id
