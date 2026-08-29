from uuid import uuid4

import pytest
from pydantic import ValidationError

from src.domain.contracts import ProfileChangeProposal, ProposalOperation, ProposalStatus


def valid_proposal_payload() -> dict[str, object]:
    return {
        "proposal_id": str(uuid4()),
        "profile_id": str(uuid4()),
        "user_id": str(uuid4()),
        "base_profile_revision": 2,
        "operation": "REPLACE",
        "field_path": "/hard_constraints/0",
        "old_value": "Hybrid within the Netherlands",
        "new_value": "Remote within the Netherlands",
        "rationale": "The candidate directly clarified the preference.",
        "evidence_references": [{"evidence_id": str(uuid4())}],
        "source_type": "USER_STATED",
        "confidence": 1.0,
        "created_at": "2026-08-29T12:00:00Z",
    }


def test_profile_change_proposal_keeps_an_auditable_change() -> None:
    proposal = ProfileChangeProposal.model_validate(valid_proposal_payload())

    assert proposal.operation is ProposalOperation.REPLACE
    assert proposal.status is ProposalStatus.PENDING
    assert proposal.field_path == "/hard_constraints/0"


@pytest.mark.parametrize(
    "field_path",
    ["", "/", "hard_constraints/0", "/hard~constraint", "/hard~2constraint"],
)
def test_profile_change_proposal_rejects_invalid_json_pointer_paths(field_path: str) -> None:
    with pytest.raises(ValidationError):
        ProfileChangeProposal.model_validate({**valid_proposal_payload(), "field_path": field_path})


def test_profile_change_proposal_supports_all_approved_operations_and_statuses() -> None:
    for operation in ProposalOperation:
        proposal = ProfileChangeProposal.model_validate(
            {**valid_proposal_payload(), "operation": operation}
        )
        assert proposal.operation is operation

    for status in ProposalStatus:
        proposal = ProfileChangeProposal.model_validate({**valid_proposal_payload(), "status": status})
        assert proposal.status is status


def test_profile_change_proposal_requires_evidence_and_valid_confidence() -> None:
    with pytest.raises(ValidationError):
        ProfileChangeProposal.model_validate({**valid_proposal_payload(), "evidence_references": []})

    with pytest.raises(ValidationError):
        ProfileChangeProposal.model_validate({**valid_proposal_payload(), "confidence": 1.1})
