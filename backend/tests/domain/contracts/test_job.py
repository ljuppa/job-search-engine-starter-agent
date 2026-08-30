from uuid import uuid4

import pytest
from pydantic import ValidationError

from src.domain.contracts import Job, JobProfile, RawJob, WorkModel


def valid_raw_job_payload() -> dict[str, object]:
    return {
        "raw_job_id": str(uuid4()),
        "source_name": "Greenhouse",
        "external_id": "eng-123",
        "source_url": "https://jobs.example.test/eng-123",
        "retrieved_at": "2026-08-30T10:00:00Z",
        "published_at": "2026-08-29T10:00:00Z",
        "title": "Engineering Director",
        "company_name": "Example Systems",
        "location": "Eindhoven, Netherlands",
        "description": "Lead a software engineering organisation.",
        "source_payload": {"posting": {"id": "eng-123"}},
        "content_hash": "sha256:abc123",
    }


def valid_job_payload() -> dict[str, object]:
    return {
        "job_id": str(uuid4()),
        "canonical_key": "example-systems:engineering-director:eindhoven",
        "raw_job_ids": [str(uuid4())],
        "created_at": "2026-08-30T10:00:00Z",
        "updated_at": "2026-08-30T10:00:00Z",
    }


def valid_job_profile_payload() -> dict[str, object]:
    return {
        "job_profile_id": str(uuid4()),
        "job_id": str(uuid4()),
        "revision": 1,
        "analysed_at": "2026-08-30T10:00:00Z",
        "role_family": "Engineering leadership",
        "seniority": "Director",
        "leadership_scope": "Multi-team organisation",
        "leader_of_leaders": True,
        "requirements": ["Experience leading engineering managers"],
        "responsibilities": ["Set engineering delivery direction"],
        "technical_expectations": ["Software architecture oversight"],
        "domains": ["Semiconductor manufacturing"],
        "work_model": "HYBRID",
        "unknown_fields": ["Compensation"],
        "confidence_map": {"seniority": 0.9, "compensation": 0.0},
    }


def test_raw_job_round_trips_as_a_global_source_record() -> None:
    raw_job = RawJob.model_validate(valid_raw_job_payload())

    restored = RawJob.model_validate_json(raw_job.model_dump_json())

    assert restored.external_id == "eng-123"
    assert not hasattr(restored, "user_id")


def test_job_references_unique_raw_source_records() -> None:
    job = Job.model_validate(valid_job_payload())

    assert len(job.raw_job_ids) == 1

    payload = valid_job_payload()
    payload["raw_job_ids"] = [payload["raw_job_ids"][0], payload["raw_job_ids"][0]]
    with pytest.raises(ValidationError):
        Job.model_validate(payload)


def test_global_job_contracts_reject_user_ownership() -> None:
    for contract, payload in (
        (RawJob, valid_raw_job_payload()),
        (Job, valid_job_payload()),
        (JobProfile, valid_job_profile_payload()),
    ):
        with pytest.raises(ValidationError):
            contract.model_validate({**payload, "user_id": str(uuid4())})


def test_job_profile_is_versioned_and_tracks_unknowns() -> None:
    profile = JobProfile.model_validate(valid_job_profile_payload())

    assert profile.work_model is WorkModel.HYBRID
    assert profile.unknown_fields == ["Compensation"]

    with pytest.raises(ValidationError):
        JobProfile.model_validate({**valid_job_profile_payload(), "revision": 0})


@pytest.mark.parametrize(
    "compensation",
    [
        {"minimum_annual_amount": 100000},
        {"currency": "EUR", "minimum_annual_amount": 120000, "maximum_annual_amount": 100000},
    ],
)
def test_job_profile_rejects_invalid_compensation(compensation: dict[str, object]) -> None:
    with pytest.raises(ValidationError):
        JobProfile.model_validate({**valid_job_profile_payload(), "compensation": compensation})
