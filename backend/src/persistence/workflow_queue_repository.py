"""PostgreSQL-backed durable queue; workers claim tasks with row locking."""

from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.domain.contracts import QueueStatus, WorkflowTask

from .models import WorkflowTaskRecord


class WorkflowQueueRepository:
    def __init__(self, session_factory: Callable[[], Session]) -> None:
        self._session_factory = session_factory

    def enqueue(self, task: WorkflowTask) -> None:
        with self._session_factory() as session:
            if session.get(WorkflowTaskRecord, task.task_id):
                raise ValueError("workflow tasks are immutable at enqueue")
            session.add(
                WorkflowTaskRecord(
                    task_id=task.task_id,
                    workflow_run_id=task.workflow_run_id,
                    workflow_name=task.workflow_name,
                    status=task.status.value,
                    attempt_count=task.attempt_count,
                    max_attempts=task.max_attempts,
                    available_at=task.available_at,
                    error_code=task.error_code,
                    payload=task.payload,
                )
            )
            session.commit()

    def claim_next(self, now: datetime) -> WorkflowTask | None:
        with self._session_factory() as session:
            record = session.scalar(
                select(WorkflowTaskRecord)
                .where(
                    WorkflowTaskRecord.status == QueueStatus.READY.value,
                    WorkflowTaskRecord.available_at <= now,
                )
                .order_by(WorkflowTaskRecord.available_at, WorkflowTaskRecord.task_id)
                .limit(1)
                .with_for_update(skip_locked=True)
            )
            if record is None:
                return None
            record.status = QueueStatus.RUNNING.value
            record.attempt_count += 1
            session.commit()
            return self._task(record)

    def complete(self, task_id: UUID) -> None:
        self._set_terminal(task_id, QueueStatus.SUCCEEDED, None)

    def retry_or_fail(self, task_id: UUID, *, error_code: str, now: datetime) -> None:
        with self._session_factory() as session:
            record = session.get(WorkflowTaskRecord, task_id)
            if record is None or record.status != QueueStatus.RUNNING.value:
                raise ValueError("only claimed workflow tasks may be retried")
            record.error_code = error_code
            if record.attempt_count >= record.max_attempts:
                record.status = QueueStatus.FAILED.value
            else:
                record.status = QueueStatus.READY.value
                record.available_at = now + timedelta(
                    seconds=retry_delay_seconds(record.attempt_count)
                )
            session.commit()

    def _set_terminal(self, task_id: UUID, status: QueueStatus, error_code: str | None) -> None:
        with self._session_factory() as session:
            record = session.get(WorkflowTaskRecord, task_id)
            if record is None or record.status != QueueStatus.RUNNING.value:
                raise ValueError("only claimed workflow tasks may be completed")
            record.status, record.error_code = status.value, error_code
            session.commit()

    @staticmethod
    def _task(record: WorkflowTaskRecord) -> WorkflowTask:
        available_at = record.available_at
        if available_at.tzinfo is None:
            available_at = available_at.replace(tzinfo=UTC)
        return WorkflowTask.model_validate(
            {
                "task_id": record.task_id,
                "workflow_run_id": record.workflow_run_id,
                "workflow_name": record.workflow_name,
                "payload": record.payload,
                "status": record.status,
                "attempt_count": record.attempt_count,
                "max_attempts": record.max_attempts,
                "available_at": available_at,
                "error_code": record.error_code,
            }
        )


def retry_delay_seconds(attempt_count: int) -> int:
    return min(60, 2 ** max(0, attempt_count - 1))
