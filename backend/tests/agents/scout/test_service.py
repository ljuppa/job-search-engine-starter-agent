from datetime import UTC, datetime
from uuid import uuid4

import pytest

from src.agents.scout.service import ScoutService, normalise_source_error
from src.domain.contracts import Job, RawJob


def raw_job(
    *, source: str = "greenhouse", external_id: str = "101", content_hash: str = "one"
) -> RawJob:
    return RawJob(
        raw_job_id=uuid4(),
        source_name=source,
        external_id=external_id,
        source_url=f"https://example.com/{source}/{external_id}",
        retrieved_at=datetime.now(UTC),
        title="Engineering Manager",
        company_name="Example",
        location="Amsterdam",
        description="Lead a team",
        source_payload={},
        content_hash=content_hash,
    )


class InMemoryJobs:
    def __init__(self) -> None:
        self.raw_by_revision = {}
        self.jobs = {}

    def save_raw_job(self, raw: RawJob) -> RawJob:
        return self.raw_by_revision.setdefault(
            (raw.source_name, raw.external_id, raw.content_hash), raw
        )

    def get_job_by_canonical_key(self, key: str) -> Job | None:
        return self.jobs.get(key)

    def get_job_by_source_identity(self, source_name: str, external_id: str) -> Job | None:
        raw_ids = {
            raw.raw_job_id
            for (stored_source, stored_external_id, _), raw in self.raw_by_revision.items()
            if (stored_source, stored_external_id) == (source_name, external_id)
        }
        return next(
            (job for job in self.jobs.values() if raw_ids.intersection(job.raw_job_ids)), None
        )

    def save_job(self, job: Job) -> None:
        self.jobs[job.canonical_key] = job

    def link_raw_job(self, job: Job, raw_job_id, *, linked_at):
        if raw_job_id in job.raw_job_ids:
            return job
        linked = job.model_copy(
            update={"raw_job_ids": [*job.raw_job_ids, raw_job_id], "updated_at": linked_at}
        )
        self.jobs[linked.canonical_key] = linked
        return linked


class RecordingHealth:
    def __init__(self) -> None:
        self.records = []

    def record(self, **record) -> None:
        self.records.append(record)


def test_repeated_source_revision_is_idempotent_and_changed_content_is_immutable_revision() -> None:
    repository = InMemoryJobs()
    service = ScoutService(repository, now=lambda: datetime(2026, 9, 26, tzinfo=UTC))

    original = service.ingest(raw_job())
    replay = service.ingest(raw_job())
    changed = service.ingest(
        raw_job(content_hash="two").model_copy(update={"title": "Senior Engineering Manager"})
    )

    assert replay.raw_job_ids == original.raw_job_ids
    assert changed.job_id == original.job_id
    assert len(changed.raw_job_ids) == 2
    assert len(repository.raw_by_revision) == 2


def test_cross_source_duplicate_links_to_existing_canonical_job() -> None:
    repository = InMemoryJobs()
    service = ScoutService(repository)

    first = service.ingest(raw_job(source="greenhouse"))
    duplicate = service.ingest(raw_job(source="lever", external_id="other"))

    assert duplicate.job_id == first.job_id
    assert len(duplicate.raw_job_ids) == 2


@pytest.mark.asyncio
async def test_source_health_records_normalised_success_and_failure() -> None:
    health = RecordingHealth()
    service = ScoutService(InMemoryJobs(), health)

    result = await service.ingest_source("greenhouse", lambda: _one_raw_job())
    assert len(result) == 1
    assert health.records[0]["status"] == "success"
    assert health.records[0]["item_count"] == 1
    assert health.records[0]["error_code"] is None

    async def unavailable():
        raise TimeoutError("the provider response contained a secret")

    with pytest.raises(TimeoutError):
        await service.ingest_source("greenhouse", unavailable)
    assert health.records[1]["status"] == "failure"
    assert health.records[1]["error_code"] == "timeout"
    assert health.records[1]["item_count"] == 0


async def _one_raw_job() -> list[RawJob]:
    return [raw_job()]


def test_source_error_normalisation_is_stable_and_non_sensitive() -> None:
    assert normalise_source_error(ConnectionError("host details")) == "connection_error"
    assert normalise_source_error(ValueError("payload details")) == "invalid_payload"
    assert normalise_source_error(RuntimeError("internal details")) == "unexpected_error"
