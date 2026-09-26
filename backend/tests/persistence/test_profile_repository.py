from datetime import UTC, datetime
from uuid import UUID, uuid4

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.domain.contracts import CandidateProfile, ProfileEvidence, ProfileStatus
from src.persistence.models import Base
from src.persistence.profile_repository import ProfileRepository


def test_repository_stores_and_reads_immutable_profile_snapshot() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    repository = ProfileRepository(sessionmaker(bind=engine, expire_on_commit=False))
    profile = CandidateProfile(
        user_id=UUID("11111111-1111-4111-8111-111111111111"), profile_id=uuid4(), revision=1,
        profile_status=ProfileStatus.DRAFT, target_roles=["Engineering Manager"],
    )

    repository.save_profile(profile)

    assert repository.get_profile(user_id=profile.user_id, profile_id=profile.profile_id) == profile
    with pytest.raises(ValueError, match="immutable"):
        repository.save_profile(profile)


def test_repository_links_evidence_to_an_exact_profile_revision() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    repository = ProfileRepository(sessionmaker(bind=engine, expire_on_commit=False))
    profile = CandidateProfile(user_id=uuid4(), profile_id=uuid4(), revision=1, profile_status=ProfileStatus.DRAFT)
    repository.save_profile(profile)

    repository.save_evidence(
        ProfileEvidence(evidence_id=uuid4(), user_id=profile.user_id, source_type="CV", source_reference="cv.pdf", captured_claim="Managed a team", confidence=0.9, captured_at=datetime.now(UTC)),
        profile_id=profile.profile_id, profile_revision=profile.revision,
    )
