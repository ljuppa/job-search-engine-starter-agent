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

    def save_raw_job(self, raw_job: RawJob) -> RawJob:
        """Store a raw revision, returning the prior revision for an exact replay."""
        with self._session_factory() as session:
            record = session.scalar(
                select(RawJobRecord).where(
                    RawJobRecord.source_name == raw_job.source_name,
                    RawJobRecord.external_id == raw_job.external_id,
                    RawJobRecord.content_hash == raw_job.content_hash,
                )
            )
            if record is not None:
                return RawJob.model_validate(record.snapshot)
            session.add(
                RawJobRecord(
                    raw_job_id=raw_job.raw_job_id,
                    source_name=raw_job.source_name,
                    external_id=raw_job.external_id,
                    source_url=str(raw_job.source_url),
                    retrieved_at=raw_job.retrieved_at,
                    content_hash=raw_job.content_hash,
                    snapshot=raw_job.model_dump(mode="json"),
                )
            )
            session.commit()
            return raw_job

    def save_job(self, job: Job) -> None:
        with self._session_factory() as session:
            if session.get(JobRecord, job.job_id) is not None:
                raise ValueError("canonical jobs are immutable")
            session.add(
                JobRecord(
                    job_id=job.job_id,
                    canonical_key=job.canonical_key,
                    snapshot=job.model_dump(mode="json"),
                )
            )
            session.commit()

    def get_job_by_canonical_key(self, canonical_key: str) -> Job | None:
        with self._session_factory() as session:
            record = session.scalar(
                select(JobRecord).where(JobRecord.canonical_key == canonical_key)
            )
            return Job.model_validate(record.snapshot) if record else None

    def get_job_by_source_identity(self, source_name: str, external_id: str) -> Job | None:
        """Find the canonical job already linked to an external source record.

        The initial schema stores canonical membership in an immutable raw-id list
        inside the canonical snapshot. This lookup preserves that identity when a
        publisher edits a title, location, or description and therefore changes
        the canonical key derived from the latest source revision.
        """
        with self._session_factory() as session:
            raw_job_ids = set(
                session.scalars(
                    select(RawJobRecord.raw_job_id).where(
                        RawJobRecord.source_name == source_name,
                        RawJobRecord.external_id == external_id,
                    )
                )
            )
            if not raw_job_ids:
                return None
            for record in session.scalars(select(JobRecord)):
                job = Job.model_validate(record.snapshot)
                if raw_job_ids.intersection(job.raw_job_ids):
                    return job
            return None

    def link_raw_job(self, job: Job, raw_job_id: UUID, *, linked_at) -> Job:
        """Link a raw revision to its canonical job exactly once.

        Raw records remain immutable.  The canonical aggregate is the deliberate
        place where the membership list is extended for another source/revision.
        """
        with self._session_factory() as session:
            record = session.get(JobRecord, job.job_id)
            if record is None:
                raise ValueError("canonical job does not exist")
            current = Job.model_validate(record.snapshot)
            if raw_job_id in current.raw_job_ids:
                return current
            linked = current.model_copy(
                update={"raw_job_ids": [*current.raw_job_ids, raw_job_id], "updated_at": linked_at}
            )
            record.snapshot = linked.model_dump(mode="json")
            session.commit()
            return linked

    def next_job_profile_revision(self, job_id: UUID) -> int:
        with self._session_factory() as session:
            maximum = session.scalar(
                select(func.max(JobProfileRecord.revision)).where(JobProfileRecord.job_id == job_id)
            )
            return (maximum or 0) + 1

    def save_job_profile(self, profile: JobProfile, *, raw_job_id: UUID) -> None:
        with self._session_factory() as session:
            session.add(
                JobProfileRecord(
                    job_profile_id=profile.job_profile_id,
                    job_id=profile.job_id,
                    revision=profile.revision,
                    raw_job_id=raw_job_id,
                    analysed_at=profile.analysed_at,
                    snapshot=profile.model_dump(mode="json"),
                )
            )
            session.commit()
