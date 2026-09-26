from collections.abc import Callable
from datetime import datetime
from uuid import uuid4

from sqlalchemy.orm import Session

from .source_health import SourceHealthRecord


class SourceHealthRepository:
    def __init__(self, session_factory: Callable[[], Session]) -> None:
        self._session_factory = session_factory

    def record(
        self,
        *,
        source_name: str,
        status: str,
        observed_at: datetime,
        item_count: int,
        latency_ms: int,
        error_code: str | None = None,
    ) -> None:
        with self._session_factory() as session:
            session.add(
                SourceHealthRecord(
                    source_health_id=uuid4(),
                    source_name=source_name,
                    status=status,
                    observed_at=observed_at,
                    item_count=item_count,
                    latency_ms=latency_ms,
                    error_code=error_code,
                )
            )
            session.commit()
