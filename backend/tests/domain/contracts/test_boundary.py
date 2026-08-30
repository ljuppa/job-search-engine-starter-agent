"""Milestone-level proof of the canonical domain-contract boundary."""

from pathlib import Path

import pytest
from pydantic import BaseModel

from src.domain.contracts import (
    Assessment,
    CandidateProfile,
    ExecutionContext,
    Job,
    JobProfile,
    ProfileChangeProposal,
    ProfileEvidence,
    RawJob,
    Recommendation,
    UserFeedback,
)

LOCAL_EXAMPLE_DIRECTORY = Path(__file__).resolve().parents[4] / "data" / "schemas"
CONTAINER_EXAMPLE_DIRECTORY = Path("/app/data/schemas")
EXAMPLE_DIRECTORY = (
    LOCAL_EXAMPLE_DIRECTORY if LOCAL_EXAMPLE_DIRECTORY.is_dir() else CONTAINER_EXAMPLE_DIRECTORY
)

ROOT_CONTRACTS: dict[str, type[BaseModel]] = {
    "assessment.example.json": Assessment,
    "candidate_profile.example.json": CandidateProfile,
    "execution_context.example.json": ExecutionContext,
    "job.example.json": Job,
    "job_profile.example.json": JobProfile,
    "profile_change_proposal.example.json": ProfileChangeProposal,
    "profile_evidence.example.json": ProfileEvidence,
    "raw_job.example.json": RawJob,
    "recommendation.example.json": Recommendation,
    "user_feedback.example.json": UserFeedback,
}


@pytest.mark.parametrize("filename, contract", ROOT_CONTRACTS.items())
def test_each_root_contract_has_a_versioned_schema_and_synthetic_example(
    filename: str, contract: type[BaseModel]
) -> None:
    schema = contract.model_json_schema()

    assert schema["properties"]["schema_version"]["default"] == "1.0"
    assert (EXAMPLE_DIRECTORY / filename).is_file()


def test_global_job_contracts_cannot_be_user_scoped() -> None:
    for contract in (RawJob, Job, JobProfile):
        assert "user_id" not in contract.model_fields


def test_private_contracts_always_carry_user_ownership() -> None:
    for contract in (
        CandidateProfile,
        ProfileEvidence,
        ProfileChangeProposal,
        Assessment,
        Recommendation,
        UserFeedback,
    ):
        assert "user_id" in contract.model_fields


def test_execution_context_keeps_scope_explicit_instead_of_inferred() -> None:
    assert {"scope", "user_id"}.issubset(ExecutionContext.model_fields)
