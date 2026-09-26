from datetime import UTC, datetime
from uuid import uuid4

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.domain.contracts import Assessment, AssessmentType
from src.persistence.assessment_repository import AssessmentRepository
from src.persistence.models import Base


def test_assessments_are_user_scoped_and_immutable() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    repository = AssessmentRepository(sessionmaker(bind=engine, expire_on_commit=False))
    assessment = Assessment(assessment_id=uuid4(), assessment_type=AssessmentType.FIT, user_id=uuid4(), job_id=uuid4(), candidate_profile_id=uuid4(), candidate_profile_revision=1, job_profile_id=uuid4(), job_profile_revision=1, score=80, confidence=0.8, agent_run_id=uuid4(), assessed_at=datetime.now(UTC))

    repository.save(assessment)

    with pytest.raises(ValueError, match="immutable"):
        repository.save(assessment)
