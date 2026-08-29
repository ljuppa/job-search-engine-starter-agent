from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

import pytest
from pydantic import ValidationError

from src.domain.contracts import (
    EvidenceReference,
    UserScopedVersionedContract,
    UtcTimestamp,
)


class ExamplePrivateContract(UserScopedVersionedContract):
    created_at: UtcTimestamp
    evidence: EvidenceReference


def valid_payload() -> dict[str, object]:
    return {
        "user_id": str(uuid4()),
        "revision": 1,
        "created_at": "2026-08-29T14:00:00+02:00",
        "evidence": {"evidence_id": str(uuid4())},
    }


def test_contract_round_trips_and_normalizes_timestamps() -> None:
    contract = ExamplePrivateContract.model_validate(valid_payload())

    restored = ExamplePrivateContract.model_validate_json(contract.model_dump_json())

    assert restored == contract
    assert contract.created_at == datetime(2026, 8, 29, 12, 0, tzinfo=UTC)
    assert isinstance(contract.user_id, UUID)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("schema_version", "0.9"),
        ("revision", 0),
        ("user_id", "not-a-uuid"),
        ("created_at", "2026-08-29T12:00:00"),
    ],
)
def test_contract_rejects_invalid_shared_primitives(field: str, value: object) -> None:
    payload = valid_payload()
    payload[field] = value

    with pytest.raises(ValidationError):
        ExamplePrivateContract.model_validate(payload)


def test_contract_rejects_unknown_fields() -> None:
    payload = valid_payload()
    payload["unexpected"] = True

    with pytest.raises(ValidationError):
        ExamplePrivateContract.model_validate(payload)


def test_utc_timestamp_accepts_an_existing_utc_datetime() -> None:
    contract = ExamplePrivateContract.model_validate(
        {
            **valid_payload(),
            "created_at": datetime(2026, 8, 29, 12, 0, tzinfo=UTC) + timedelta(seconds=1),
        }
    )

    assert contract.created_at.tzinfo is UTC
