"""Relational metadata and immutable JSON snapshots for candidate profiles."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, ForeignKeyConstraint, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.types import JSON

JSON_DOCUMENT = JSON().with_variant(JSONB, "postgresql")


class Base(DeclarativeBase):
    pass


class CandidateProfileRecord(Base):
    __tablename__ = "candidate_profile_revisions"

    profile_id: Mapped[UUID] = mapped_column(primary_key=True)
    revision: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[UUID] = mapped_column(index=True)
    profile_status: Mapped[str] = mapped_column(String(32), index=True)
    snapshot: Mapped[dict] = mapped_column(JSON_DOCUMENT)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class ProfileEvidenceRecord(Base):
    __tablename__ = "profile_evidence"
    __table_args__ = (
        ForeignKeyConstraint(
            ["profile_id", "profile_revision"],
            ["candidate_profile_revisions.profile_id", "candidate_profile_revisions.revision"],
        ),
    )

    evidence_id: Mapped[UUID] = mapped_column(primary_key=True)
    user_id: Mapped[UUID] = mapped_column(index=True)
    profile_id: Mapped[UUID] = mapped_column()
    profile_revision: Mapped[int] = mapped_column()
    source_type: Mapped[str] = mapped_column(String(32))
    source_reference: Mapped[str] = mapped_column(Text)
    captured_claim: Mapped[str] = mapped_column(Text)
    confidence: Mapped[float] = mapped_column()
    captured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class ProfileChangeProposalRecord(Base):
    __tablename__ = "profile_change_proposals"
    __table_args__ = (
        UniqueConstraint("proposal_id", name="uq_profile_change_proposals_proposal_id"),
        ForeignKeyConstraint(
            ["profile_id", "base_profile_revision"],
            ["candidate_profile_revisions.profile_id", "candidate_profile_revisions.revision"],
        ),
    )

    proposal_id: Mapped[UUID] = mapped_column(primary_key=True)
    user_id: Mapped[UUID] = mapped_column(index=True)
    profile_id: Mapped[UUID] = mapped_column()
    base_profile_revision: Mapped[int] = mapped_column()
    operation: Mapped[str] = mapped_column(String(16))
    field_path: Mapped[str] = mapped_column(Text)
    old_value: Mapped[object | None] = mapped_column(JSON_DOCUMENT, nullable=True)
    new_value: Mapped[object | None] = mapped_column(JSON_DOCUMENT, nullable=True)
    rationale: Mapped[str] = mapped_column(Text)
    evidence_ids: Mapped[list[str]] = mapped_column(JSON_DOCUMENT)
    source_type: Mapped[str] = mapped_column(String(32))
    confidence: Mapped[float] = mapped_column()
    status: Mapped[str] = mapped_column(String(32), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class RawJobRecord(Base):
    __tablename__ = "raw_jobs"

    raw_job_id: Mapped[UUID] = mapped_column(primary_key=True)
    source_name: Mapped[str] = mapped_column(String(128))
    external_id: Mapped[str] = mapped_column(String(256))
    source_url: Mapped[str] = mapped_column(Text)
    retrieved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    content_hash: Mapped[str] = mapped_column(String(256), index=True)
    snapshot: Mapped[dict] = mapped_column(JSON_DOCUMENT)


class JobRecord(Base):
    __tablename__ = "jobs"

    job_id: Mapped[UUID] = mapped_column(primary_key=True)
    canonical_key: Mapped[str] = mapped_column(String(512), unique=True)
    snapshot: Mapped[dict] = mapped_column(JSON_DOCUMENT)


class JobProfileRecord(Base):
    __tablename__ = "job_profile_revisions"
    __table_args__ = (
        ForeignKeyConstraint(["job_id"], ["jobs.job_id"]),
        ForeignKeyConstraint(["raw_job_id"], ["raw_jobs.raw_job_id"]),
    )

    job_profile_id: Mapped[UUID] = mapped_column(primary_key=True)
    job_id: Mapped[UUID] = mapped_column(index=True)
    revision: Mapped[int] = mapped_column()
    raw_job_id: Mapped[UUID] = mapped_column()
    analysed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    snapshot: Mapped[dict] = mapped_column(JSON_DOCUMENT)

    __table_args__ = __table_args__ + (UniqueConstraint("job_id", "revision", name="uq_job_profile_revision"),)
