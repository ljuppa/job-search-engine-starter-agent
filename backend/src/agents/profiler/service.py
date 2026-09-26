"""Deterministic application service for the non-mutating Profiler boundary."""

from copy import deepcopy
from datetime import UTC, datetime
from typing import Protocol
from uuid import UUID, uuid4

from src.domain.contracts import (
    CandidateProfile,
    EvidenceReference,
    ProfileChangeProposal,
    ProfileEvidence,
    ProfileStatus,
    ProposalOperation,
    ProposalStatus,
)
from src.persistence.profile_repository import ProfileRepository

from .contracts import (
    ProfileChangeDraft,
    ProfileFact,
    ProfilerInput,
    ProfilerQuestion,
    ProfilerResult,
)


class ProfilerExtractor(Protocol):
    async def extract(self, profiler_input: ProfilerInput) -> ProfilerResult: ...


def _segments(pointer: str) -> list[str]:
    return [segment.replace("~1", "/").replace("~0", "~") for segment in pointer.split("/")[1:]]


def _read_pointer(document: dict, pointer: str) -> object | None:
    current: object = document
    for segment in _segments(pointer):
        if isinstance(current, dict):
            if segment not in current:
                return None
            current = current[segment]
        elif isinstance(current, list) and segment.isdigit() and int(segment) < len(current):
            current = current[int(segment)]
        else:
            return None
    return current


def _write_pointer(document: dict, pointer: str, value: object) -> None:
    segments = _segments(pointer)
    current: object = document
    for segment in segments[:-1]:
        if isinstance(current, dict):
            nested = current.get(segment)
            if nested is None:
                nested = {}
                current[segment] = nested
            current = nested
        elif isinstance(current, list) and segment.isdigit() and int(segment) < len(current):
            current = current[int(segment)]
        else:
            raise ValueError("JSON pointer cannot create this intermediate path")
    if isinstance(current, list):
        if segments[-1] == "-":
            current.append(value)
        elif segments[-1].isdigit():
            current[int(segments[-1])] = value
        else:
            raise ValueError("JSON pointer list segment must be an array index")
    elif isinstance(current, dict):
        current[segments[-1]] = value
    else:
        raise TypeError("JSON pointer target must be an object or array")


def _remove_pointer(document: dict, pointer: str) -> None:
    segments = _segments(pointer)
    current: object = document
    for segment in segments[:-1]:
        if isinstance(current, dict):
            current = current[segment]
        elif isinstance(current, list) and segment.isdigit():
            current = current[int(segment)]
        else:
            raise ValueError("JSON pointer does not identify an existing value")
    if isinstance(current, dict):
        del current[segments[-1]]
    elif isinstance(current, list) and segments[-1].isdigit():
        del current[int(segments[-1])]
    else:
        raise ValueError("JSON pointer does not identify a removable value")


def _ensure_mutable_profile_path(pointer: str) -> None:
    allowed_roots = {
        "search_posture", "summary", "career_history", "capabilities", "achievements",
        "target_roles", "acceptable_roles", "excluded_roles", "hard_constraints",
        "soft_preferences", "career_goals", "strengths", "gaps", "location_preferences",
        "compensation_preferences", "work_model_preferences", "confidence_map",
    }
    if _segments(pointer)[0] not in allowed_roots:
        raise ValueError("Profiler may not change profile identity, revision, or status fields")


class ProfilerService:
    """Persists extracted evidence and makes profile changes auditable proposals."""

    def __init__(self, repository: ProfileRepository, extractor: ProfilerExtractor) -> None:
        self._repository = repository
        self._extractor = extractor

    async def run(self, profiler_input: ProfilerInput) -> ProfilerResult:
        result = await self._extractor.extract(profiler_input)
        profile = profiler_input.current_profile or self._new_draft(profiler_input)

        if profiler_input.current_profile is None:
            profile = self._apply_facts_to_draft(profile, result.facts)
            self._repository.save_profile(profile)

        evidence_by_source = self._persist_evidence(profile, profiler_input, result.facts)

        for draft in result.change_drafts:
            self._persist_proposal(profile, draft, evidence_by_source, profiler_input)
        return ProfilerResult(
            facts=result.facts,
            change_drafts=result.change_drafts,
            questions=self.required_questions(profile),
        )

    def accept_proposal(self, proposal: ProfileChangeProposal, current_profile: CandidateProfile) -> CandidateProfile:
        """Create a new profile revision; never mutate a confirmed snapshot."""

        if proposal.status is not ProposalStatus.PENDING:
            raise ValueError("only pending proposals may be accepted")
        if (proposal.user_id, proposal.profile_id, proposal.base_profile_revision) != (
            current_profile.user_id, current_profile.profile_id, current_profile.revision,
        ):
            raise ValueError("proposal must target the exact current profile revision")
        document = deepcopy(current_profile.model_dump(mode="json"))
        _ensure_mutable_profile_path(proposal.field_path)
        if proposal.operation is ProposalOperation.REMOVE:
            _remove_pointer(document, proposal.field_path)
        else:
            _write_pointer(document, proposal.field_path, proposal.new_value)
        document["revision"] = current_profile.revision + 1
        document["profile_status"] = ProfileStatus.CONFIRMED.value
        updated = CandidateProfile.model_validate(document)
        self._repository.save_profile(updated)
        self._repository.resolve_proposal(
            proposal.proposal_id,
            user_id=proposal.user_id,
            status=ProposalStatus.USER_ACCEPTED.value,
            resolved_at=datetime.now(UTC),
        )
        return updated

    @staticmethod
    def required_questions(profile: CandidateProfile) -> list[ProfilerQuestion]:
        from .questions import missing_hard_constraint_questions

        return missing_hard_constraint_questions(profile)

    def _new_draft(self, profiler_input: ProfilerInput) -> CandidateProfile:
        return CandidateProfile(
            profile_id=uuid4(), user_id=profiler_input.context.user_id,
            revision=1, profile_status=ProfileStatus.DRAFT,
        )

    def _apply_facts_to_draft(self, profile: CandidateProfile, facts: list[ProfileFact]) -> CandidateProfile:
        document = profile.model_dump(mode="json")
        for fact in facts:
            _ensure_mutable_profile_path(fact.field_path)
            _write_pointer(document, fact.field_path, fact.value)
        return CandidateProfile.model_validate(document)

    def _persist_evidence(
        self, profile: CandidateProfile, profiler_input: ProfilerInput, facts: list[ProfileFact]
    ) -> dict[UUID, list[ProfileEvidence]]:
        sources = {source.source_id: source for source in profiler_input.sources}
        evidence_by_source: dict[UUID, list[ProfileEvidence]] = {}
        for fact in facts:
            for source_id in fact.source_ids:
                source = sources[source_id]
                evidence = ProfileEvidence(
                    evidence_id=uuid4(), user_id=profile.user_id, source_type=source.source_type,
                    source_reference=source.source_reference, captured_claim=f"{fact.field_path}: {fact.value}",
                    confidence=fact.confidence, captured_at=datetime.now(UTC),
                )
                self._repository.save_evidence(evidence, profile_id=profile.profile_id, profile_revision=profile.revision)
                evidence_by_source.setdefault(source_id, []).append(evidence)
        return evidence_by_source

    def _persist_proposal(
        self, profile: CandidateProfile, draft: ProfileChangeDraft,
        evidence_by_source: dict[UUID, list[ProfileEvidence]], profiler_input: ProfilerInput,
    ) -> None:
        _ensure_mutable_profile_path(draft.field_path)
        references = [EvidenceReference(evidence_id=evidence.evidence_id) for source_id in draft.source_ids for evidence in evidence_by_source.get(source_id, [])]
        if not references:
            raise ValueError("profile change drafts must reference extracted evidence")
        source_type = next(source.source_type for source in profiler_input.sources if source.source_id == draft.source_ids[0])
        proposal = ProfileChangeProposal(
            proposal_id=uuid4(), user_id=profile.user_id, profile_id=profile.profile_id,
            base_profile_revision=profile.revision, operation=draft.operation, field_path=draft.field_path,
            old_value=_read_pointer(profile.model_dump(mode="json"), draft.field_path), new_value=draft.new_value,
            rationale=draft.rationale, evidence_references=references, source_type=source_type,
            confidence=draft.confidence, status=ProposalStatus.PENDING, created_at=datetime.now(UTC),
        )
        self._repository.save_proposal(proposal)
