from datetime import UTC, datetime, timedelta
from uuid import uuid4

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.domain.contracts import WorkflowTask
from src.persistence.models import Base
from src.persistence.workflow_queue_repository import WorkflowQueueRepository, retry_delay_seconds


def task(now: datetime) -> WorkflowTask:
    return WorkflowTask(
        task_id=uuid4(),
        workflow_run_id=uuid4(),
        workflow_name="job_discovery",
        payload={"board": "example"},
        available_at=now,
    )


def test_queue_claims_retries_with_backoff_and_then_completes() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    repository = WorkflowQueueRepository(sessionmaker(bind=engine, expire_on_commit=False))
    now = datetime.now(UTC)
    queued = task(now)
    repository.enqueue(queued)

    claimed = repository.claim_next(now)
    assert claimed is not None and claimed.attempt_count == 1
    repository.retry_or_fail(claimed.task_id, error_code="timeout", now=now)
    assert repository.claim_next(now) is None
    retried = repository.claim_next(now + timedelta(seconds=1))
    assert retried is not None and retried.attempt_count == 2
    repository.complete(retried.task_id)


def test_retry_backoff_is_bounded_and_deterministic() -> None:
    assert [retry_delay_seconds(attempt) for attempt in (1, 2, 3, 10)] == [1, 2, 4, 60]
