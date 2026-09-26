from datetime import UTC, datetime

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from src.persistence.models import Base, SourceHealthRecord
from src.persistence.source_health_repository import SourceHealthRepository


def test_source_health_observations_are_persisted_with_normalised_fields() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, expire_on_commit=False)

    SourceHealthRepository(factory).record(
        source_name="greenhouse",
        status="failure",
        observed_at=datetime.now(UTC),
        item_count=0,
        latency_ms=12,
        error_code="timeout",
    )

    with factory() as session:
        record = session.scalar(select(SourceHealthRecord))
    assert record is not None
    assert (record.status, record.item_count, record.error_code) == ("failure", 0, "timeout")
