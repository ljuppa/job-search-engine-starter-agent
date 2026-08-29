from uuid import uuid4

import pytest
from pydantic import ValidationError

from src.domain.contracts import CandidateProfile, ProfileEvidence, ProfileStatus, SearchPosture


def valid_profile_payload() -> dict[str, object]:
    return {
        "profile_id": str(uuid4()),
        "user_id": str(uuid4()),
        "revision": 1,
        "profile_status": "CONFIRMED",
        "search_posture": "SELECTIVE",
        "capabilities": ["Product strategy"],
        "hard_constraints": ["Remote within the Netherlands"],
        "soft_preferences": ["B2B SaaS"],
        "compensation_preferences": {
            "currency": "EUR",
            "minimum_annual_amount": 100000,
            "target_annual_amount": 120000,
        },
        "work_model_preferences": {"acceptable_models": ["REMOTE", "HYBRID"]},
        "confidence_map": {"capabilities.0": 0.9},
    }


def valid_evidence_payload() -> dict[str, object]:
    return {
        "evidence_id": str(uuid4()),
        "user_id": str(uuid4()),
        "source_type": "CV",
        "source_reference": "cv:2026-08-29",
        "captured_claim": "Led a product team",
        "confidence": 0.9,
        "captured_at": "2026-08-29T12:00:00Z",
    }


def test_candidate_profile_keeps_lifecycle_and_search_posture_separate() -> None:
    profile = CandidateProfile.model_validate(valid_profile_payload())

    assert profile.profile_status is ProfileStatus.CONFIRMED
    assert profile.search_posture is SearchPosture.SELECTIVE
    assert profile.compensation_preferences.minimum_annual_amount == 100000


def test_candidate_profile_accepts_an_unknown_search_posture() -> None:
    payload = valid_profile_payload()
    payload["search_posture"] = None

    profile = CandidateProfile.model_validate(payload)

    assert profile.search_posture is None


@pytest.mark.parametrize(
    "changes",
    [
        {"profile_status": "ACTIVE"},
        {"confidence_map": {"capabilities.0": 1.1}},
        {"compensation_preferences": {"minimum_annual_amount": 100000}},
        {
            "compensation_preferences": {
                "currency": "EUR",
                "minimum_annual_amount": 120000,
                "target_annual_amount": 100000,
            }
        },
    ],
)
def test_candidate_profile_rejects_invalid_values(changes: dict[str, object]) -> None:
    with pytest.raises(ValidationError):
        CandidateProfile.model_validate({**valid_profile_payload(), **changes})


def test_profile_evidence_requires_provenance_and_valid_confidence() -> None:
    evidence = ProfileEvidence.model_validate(valid_evidence_payload())

    assert evidence.source_reference == "cv:2026-08-29"

    invalid_payload = {**valid_evidence_payload(), "confidence": -0.1}
    with pytest.raises(ValidationError):
        ProfileEvidence.model_validate(invalid_payload)
