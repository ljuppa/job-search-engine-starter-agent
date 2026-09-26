from datetime import UTC, datetime
from uuid import uuid4

from src.domain.contracts import Assessment, AssessmentType, RecommendationClassification
from src.workflows.ranking import rank_assessments


def assessment(job_id, score: int) -> Assessment:
    return Assessment(
        assessment_id=uuid4(),
        assessment_type=AssessmentType.FIT,
        user_id=uuid4(),
        job_id=job_id,
        candidate_profile_id=uuid4(),
        candidate_profile_revision=1,
        job_profile_id=uuid4(),
        job_profile_revision=1,
        score=score,
        confidence=1,
        agent_run_id=uuid4(),
        assessed_at=datetime.now(UTC),
    )


def test_ranking_is_deterministic_and_classifies_scores() -> None:
    low, high = uuid4(), uuid4()
    ranked = rank_assessments([assessment(low, 45), assessment(high, 80)])

    assert [(rank, kind) for _, rank, kind in ranked] == [
        (1, RecommendationClassification.PRIORITY),
        (2, RecommendationClassification.EXCLUDE),
    ]
