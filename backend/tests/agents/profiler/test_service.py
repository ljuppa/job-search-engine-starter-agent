from datetime import UTC, datetime
from uuid import UUID, uuid4

import pytest

from src.agents.profiler.contracts import (
    FactDisposition,
    ProfileChangeDraft,
    ProfileFact,
    ProfilerInput,
    ProfilerResult,
    ProfilerSource,
)
from src.agents.profiler.service import ProfilerService
from src.domain.contracts import (
    CandidateProfile,
    ExecutionContext,
    ExecutionScope,
    ProfileChangeProposal,
    ProfileStatus,
    ProposalOperation,
    ProposalStatus,
)

USER_ID = UUID("11111111-1111-4111-8111-111111111111")


class RecordingRepository:
    def __init__(self) -> None:
        self.profiles: list[CandidateProfile] = []
        self.evidence = []
        self.proposals: list[ProfileChangeProposal] = []
        self.resolutions = []

    def save_profile(self, profile: CandidateProfile) -> None:
        self.profiles.append(profile)

    def save_evidence(self, evidence, *, profile_id, profile_revision) -> None:
        self.evidence.append((evidence, profile_id, profile_revision))

    def save_proposal(self, proposal: ProfileChangeProposal) -> None:
        self.proposals.append(proposal)

    def resolve_proposal(self, proposal_id, *, user_id, status, resolved_at) -> None:
        self.resolutions.append((proposal_id, user_id, status, resolved_at))


class FixedExtractor:
    def __init__(self, result: ProfilerResult) -> None:
        self.result = result

    async def extract(self, profiler_input: ProfilerInput) -> ProfilerResult:
        return self.result


def context(profile: CandidateProfile | None = None) -> ExecutionContext:
    return ExecutionContext(
        correlation_id=uuid4(), trace_id=uuid4(), workflow_run_id=uuid4(), scope=ExecutionScope.USER,
        user_id=USER_ID, candidate_profile_id=profile.profile_id if profile else None,
        candidate_profile_revision=profile.revision if profile else None,
    )


def source() -> ProfilerSource:
    return ProfilerSource(source_id=uuid4(), source_type="CV", source_reference="cv.pdf", content="Target role: Engineering Manager")


@pytest.mark.asyncio
async def test_initial_extraction_creates_draft_profile_evidence_and_pending_proposal() -> None:
    supplied_source = source()
    result = ProfilerResult(
        facts=[ProfileFact(field_path="/target_roles", value=["Engineering Manager"], disposition=FactDisposition.EXTRACTED, confidence=0.9, source_ids=[supplied_source.source_id])],
        change_drafts=[ProfileChangeDraft(operation=ProposalOperation.ADD, field_path="/hard_constraints/-", new_value="Remote only", rationale="Explicitly stated in the CV", confidence=0.9, source_ids=[supplied_source.source_id])],
    )
    repository = RecordingRepository()
    service = ProfilerService(repository, FixedExtractor(result))

    returned = await service.run(ProfilerInput(context=context(), sources=[supplied_source], prompt_version="profiler.v1"))

    assert repository.profiles[0].profile_status is ProfileStatus.DRAFT
    assert repository.profiles[0].target_roles == ["Engineering Manager"]
    assert len(repository.evidence) == 1
    assert repository.proposals[0].status is ProposalStatus.PENDING
    assert returned.questions[0].topic.value == "PREFERRED_LOCATIONS"


@pytest.mark.asyncio
async def test_profiler_rejects_llm_attempts_to_change_managed_profile_fields() -> None:
    supplied_source = source()
    result = ProfilerResult(
        facts=[ProfileFact(field_path="/profile_status", value="CONFIRMED", disposition=FactDisposition.EXTRACTED, confidence=1, source_ids=[supplied_source.source_id])]
    )
    service = ProfilerService(RecordingRepository(), FixedExtractor(result))

    with pytest.raises(ValueError, match="identity, revision, or status"):
        await service.run(ProfilerInput(context=context(), sources=[supplied_source], prompt_version="profiler.v1"))


def test_acceptance_creates_a_new_confirmed_revision_without_mutating_old_profile() -> None:
    profile = CandidateProfile(user_id=USER_ID, profile_id=uuid4(), revision=1, profile_status=ProfileStatus.CONFIRMED, target_roles=["Engineering Manager"])
    proposal = ProfileChangeProposal(
        proposal_id=uuid4(), user_id=USER_ID, profile_id=profile.profile_id, base_profile_revision=1,
        operation=ProposalOperation.ADD, field_path="/hard_constraints/-", new_value="Remote only",
        rationale="Candidate confirmed this preference", evidence_references=[{"evidence_id": uuid4()}],
        source_type="USER_STATED", confidence=1, status=ProposalStatus.PENDING, created_at=datetime.now(UTC),
    )
    repository = RecordingRepository()
    service = ProfilerService(repository, FixedExtractor(ProfilerResult()))

    accepted = service.accept_proposal(proposal, profile)

    assert profile.revision == 1
    assert profile.hard_constraints == []
    assert accepted.revision == 2
    assert accepted.hard_constraints == ["Remote only"]
    assert repository.resolutions[0][2] == ProposalStatus.USER_ACCEPTED.value


def test_acceptance_honours_remove_operation() -> None:
    profile = CandidateProfile(user_id=USER_ID, profile_id=uuid4(), revision=1, profile_status=ProfileStatus.CONFIRMED, hard_constraints=["Remote only"])
    proposal = ProfileChangeProposal(
        proposal_id=uuid4(), user_id=USER_ID, profile_id=profile.profile_id, base_profile_revision=1,
        operation=ProposalOperation.REMOVE, field_path="/hard_constraints/0", rationale="Candidate withdrew it",
        evidence_references=[{"evidence_id": uuid4()}], source_type="USER_STATED", confidence=1,
        status=ProposalStatus.PENDING, created_at=datetime.now(UTC),
    )
    accepted = ProfilerService(RecordingRepository(), FixedExtractor(ProfilerResult())).accept_proposal(proposal, profile)

    assert accepted.hard_constraints == []
