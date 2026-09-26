"""Persistence boundary for shared raw jobs, canonical jobs, and analyses."""

from collections.abc import Callable
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from src.domain.contracts import Job, JobProfile, RawJob

from .models import JobProfileRecord, JobRecord, RawJobRecord


class JobRepository:
    def __init__(self, session_factory: Callable[[], Session]) -> None:
        self._session_factory = session_factory

    def save_raw_job(self, raw_job: RawJob) -> None:
        with self._session_factory() as session:
            if session.get(RawJobRecord, raw_job.raw_job_id) is not None:
                raise ValueError("raw jobs are immutable")
            session.add(RawJobRecord(raw_job_id=raw_job.raw_job_id, source_name=raw_job.source_name, external_id=raw_job.external_id, source_url=str(raw_job.source_url), retrieved_at=raw_job.retrieved_at, content_hash=raw_job.content_hash, snapshot=raw_job.model_dump(mode="json")))
            session.commit()

    def save_job(self, job: Job) -> None:
        with self._session_factory() as session:
            if session.get(JobRecord, job.job_id) is not None:
                raise ValueError("canonical jobs are immutable")
            session.add(JobRecord(job_id=job.job_id, canonical_key=job.canonical_key, snapshot=job.model_dump(mode="json")))
            session.commit()

    def next_job_profile_revision(self, job_id: UUID) -> int:
        with self._session_factory() as session:
            maximum = session.scalar(select(func.max(JobProfileRecord.revision)).where(JobProfileRecord.job_id == job_id))
            return (maximum or 0) + 1

    def save_job_profile(self, profile: JobProfile, *, raw_job_id: UUID) -> None:
        with self._session_factory() as session:
            session.add(JobProfileRecord(job_profile_id=profile.job_profile_id, job_id=profile.job_id, revision=profile.revision, raw_job_id=raw_job_id, analysed_at=profile.analysed_at, snapshot=profile.model_dump(mode="json")))
            session.commit()
