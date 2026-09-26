"""Persistence boundary for immutable user-scoped assessments."""

from collections.abc import Callable

from sqlalchemy.orm import Session

from src.domain.contracts import Assessment

from .models import AssessmentRecord


class AssessmentRepository:
    def __init__(self, session_factory: Callable[[], Session]) -> None:
        self._session_factory = session_factory

    def save(self, assessment: Assessment) -> None:
        with self._session_factory() as session:
            if session.get(AssessmentRecord, assessment.assessment_id) is not None:
                raise ValueError("assessments are immutable")
            session.add(AssessmentRecord(assessment_id=assessment.assessment_id, user_id=assessment.user_id, job_id=assessment.job_id, assessment_type=assessment.assessment_type.value, assessed_at=assessment.assessed_at, snapshot=assessment.model_dump(mode="json")))
            session.commit()
