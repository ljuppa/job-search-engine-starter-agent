"""Persistence boundary for immutable profiles, evidence, and proposals."""

from collections.abc import Callable
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.domain.contracts import CandidateProfile, ProfileChangeProposal, ProfileEvidence

from .models import CandidateProfileRecord, ProfileChangeProposalRecord, ProfileEvidenceRecord


class ProfileRepository:
    def __init__(self, session_factory: Callable[[], Session]) -> None:
        self._session_factory = session_factory

    def get_profile(self, *, user_id: UUID, profile_id: UUID, revision: int | None = None) -> CandidateProfile | None:
        with self._session_factory() as session:
            statement = select(CandidateProfileRecord).where(
                CandidateProfileRecord.user_id == user_id,
                CandidateProfileRecord.profile_id == profile_id,
            )
            if revision is None:
                statement = statement.order_by(CandidateProfileRecord.revision.desc()).limit(1)
            else:
                statement = statement.where(CandidateProfileRecord.revision == revision)
            record = session.scalar(statement)
            return CandidateProfile.model_validate(record.snapshot) if record else None

    def save_profile(self, profile: CandidateProfile) -> None:
        with self._session_factory() as session:
            existing = session.get(CandidateProfileRecord, (profile.profile_id, profile.revision))
            if existing is not None:
                raise ValueError("candidate profile revisions are immutable")
            session.add(CandidateProfileRecord(
                profile_id=profile.profile_id, revision=profile.revision, user_id=profile.user_id,
                profile_status=profile.profile_status.value, snapshot=profile.model_dump(mode="json"),
                created_at=datetime.now(UTC),
            ))
            session.commit()

    def save_evidence(self, evidence: ProfileEvidence, *, profile_id: UUID, profile_revision: int) -> None:
        with self._session_factory() as session:
            session.add(ProfileEvidenceRecord(
                evidence_id=evidence.evidence_id, user_id=evidence.user_id, profile_id=profile_id,
                profile_revision=profile_revision, source_type=evidence.source_type.value,
                source_reference=evidence.source_reference, captured_claim=evidence.captured_claim,
                confidence=evidence.confidence, captured_at=evidence.captured_at,
            ))
            session.commit()

    def save_proposal(self, proposal: ProfileChangeProposal) -> None:
        with self._session_factory() as session:
            session.add(ProfileChangeProposalRecord(
                proposal_id=proposal.proposal_id, user_id=proposal.user_id, profile_id=proposal.profile_id,
                base_profile_revision=proposal.base_profile_revision, operation=proposal.operation.value,
                field_path=proposal.field_path, old_value=proposal.old_value, new_value=proposal.new_value,
                rationale=proposal.rationale,
                evidence_ids=[str(reference.evidence_id) for reference in proposal.evidence_references],
                source_type=proposal.source_type.value, confidence=proposal.confidence,
                status=proposal.status.value, created_at=proposal.created_at, resolved_at=proposal.resolved_at,
            ))
            session.commit()

    def resolve_proposal(self, proposal_id: UUID, *, user_id: UUID, status: str, resolved_at: datetime) -> None:
        with self._session_factory() as session:
            record = session.get(ProfileChangeProposalRecord, proposal_id)
            if record is None or record.user_id != user_id:
                raise ValueError("profile change proposal was not found for this user")
            if record.status != "PENDING":
                raise ValueError("only pending profile change proposals may be resolved")
            record.status = status
            record.resolved_at = resolved_at
            session.commit()
