"""Validation of the synthetic contract examples kept at the repository boundary."""

import json
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

EXAMPLE_CONTRACTS: dict[str, type[BaseModel]] = {
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


@pytest.mark.parametrize("filename, contract", EXAMPLE_CONTRACTS.items())
def test_example_validates_against_its_canonical_contract(
    filename: str, contract: type[BaseModel]
) -> None:
    payload = json.loads((EXAMPLE_DIRECTORY / filename).read_text())

    contract.model_validate(payload)


@pytest.mark.parametrize("contract", EXAMPLE_CONTRACTS.values())
def test_public_contracts_generate_json_schema(contract: type[BaseModel]) -> None:
    schema = contract.model_json_schema()

    assert schema["title"] == contract.__name__
