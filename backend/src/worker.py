"""Durable queue worker; workflow handlers are registered by the composition root."""

import os
import signal
from datetime import UTC, datetime
from threading import Event

from src.persistence.database import create_session_factory
from src.persistence.workflow_queue_repository import WorkflowQueueRepository


def main() -> None:
    """Claim durable work; unavailable handlers are retried with a safe error code."""
    stop_event = Event()
    queue = WorkflowQueueRepository(create_session_factory(os.environ["DATABASE_URL"]))

    def stop(*_: object) -> None:
        stop_event.set()

    signal.signal(signal.SIGINT, stop)
    signal.signal(signal.SIGTERM, stop)
    print("Worker running", flush=True)
    while not stop_event.wait(1):
        task = queue.claim_next(datetime.now(UTC))
        if task is None:
            continue
        queue.retry_or_fail(
            task.task_id, error_code="handler_not_configured", now=datetime.now(UTC)
        )


if __name__ == "__main__":
    main()
