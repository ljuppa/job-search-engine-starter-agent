"""Global deterministic Scout ingestion, deduplication, and source health."""

from collections.abc import Callable
from datetime import UTC, datetime
from time import perf_counter_ns
from typing import Protocol
from uuid import uuid4

from src.domain.contracts import Job, RawJob
from src.persistence.job_repository import JobRepository


class RawJobFetcher(Protocol):
    async def __call__(self) -> list[RawJob]: ...


class SourceHealthWriter(Protocol):
    def record(
        self,
        *,
        source_name: str,
        status: str,
        observed_at: datetime,
        item_count: int,
        latency_ms: int,
        error_code: str | None = None,
    ) -> None: ...


def canonical_key(raw_job: RawJob) -> str:
    return ":".join(
        part.casefold().strip()
        for part in (raw_job.company_name, raw_job.title, raw_job.location or "")
    )


class ScoutService:
    def __init__(
        self,
        repository: JobRepository,
        source_health_repository: SourceHealthWriter | None = None,
        *,
        now: Callable[[], datetime] = lambda: datetime.now(UTC),
    ) -> None:
        self._repository = repository
        self._source_health_repository = source_health_repository
        self._now = now

    def ingest(self, raw_job: RawJob) -> Job:
        existing_source_job = self._repository.get_job_by_source_identity(
            raw_job.source_name, raw_job.external_id
        )
        persisted_raw_job = self._repository.save_raw_job(raw_job)
        if existing_source_job is not None:
            return self._repository.link_raw_job(
                existing_source_job, persisted_raw_job.raw_job_id, linked_at=self._now()
            )
        key = canonical_key(persisted_raw_job)
        existing = self._repository.get_job_by_canonical_key(key)
        if existing is not None:
            return self._repository.link_raw_job(
                existing, persisted_raw_job.raw_job_id, linked_at=self._now()
            )
        job = Job(
            job_id=uuid4(),
            canonical_key=key,
            raw_job_ids=[persisted_raw_job.raw_job_id],
            created_at=self._now(),
            updated_at=self._now(),
        )
        self._repository.save_job(job)
        return job

    async def ingest_source(self, source_name: str, fetch: RawJobFetcher) -> list[Job]:
        """Run one connector and persist one normalized health observation.

        The original connector exception is deliberately re-raised: orchestration
        needs to decide retry policy, while source health still records the failure.
        """
        started = perf_counter_ns()
        try:
            raw_jobs = await fetch()
            jobs = [self.ingest(raw_job) for raw_job in raw_jobs]
        except Exception as error:
            self._record_source_health(
                source_name=source_name,
                status="failure",
                item_count=0,
                latency_ms=_elapsed_milliseconds(started),
                error_code=normalise_source_error(error),
            )
            raise
        self._record_source_health(
            source_name=source_name,
            status="success",
            item_count=len(raw_jobs),
            latency_ms=_elapsed_milliseconds(started),
        )
        return jobs

    def _record_source_health(
        self,
        *,
        source_name: str,
        status: str,
        item_count: int,
        latency_ms: int,
        error_code: str | None = None,
    ) -> None:
        if self._source_health_repository is not None:
            self._source_health_repository.record(
                source_name=source_name,
                status=status,
                observed_at=self._now(),
                item_count=item_count,
                latency_ms=latency_ms,
                error_code=error_code,
            )


def _elapsed_milliseconds(started: int) -> int:
    return max(0, (perf_counter_ns() - started) // 1_000_000)


def normalise_source_error(error: Exception) -> str:
    """Map transport and payload failures to stable, non-sensitive error codes."""
    if isinstance(error, TimeoutError):
        return "timeout"
    if isinstance(error, (ConnectionError, OSError)):
        return "connection_error"
    if isinstance(error, (TypeError, ValueError)):
        return "invalid_payload"
    return "unexpected_error"
