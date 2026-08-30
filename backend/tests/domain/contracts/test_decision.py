from uuid import uuid4

import pytest
from pydantic import ValidationError

from src.domain.contracts import (
    Assessment,
    AssessmentType,
    FeedbackAction,
    Recommendation,
    RecommendationClassification,
    UserFeedback,
)


def versioned_input_references() -> dict[str, object]:
    return {
        "job_id": str(uuid4()),
        "candidate_profile_id": str(uuid4()),
        "candidate_profile_revision": 2,
        "job_profile_id": str(uuid4()),
        "job_profile_revision": 3,
    }


def valid_assessment_payload() -> dict[str, object]:
    return {
        "assessment_id": str(uuid4()),
        "user_id": str(uuid4()),
        "assessment_type": "FIT",
        **versioned_input_references(),
        "score": 82,
        "confidence": 0.9,
        "strengths": ["Relevant engineering leadership experience"],
        "gaps": ["No direct experience with the product domain"],
        "risks": ["Unclear relocation requirement"],
        "evidence_references": [{"evidence_id": str(uuid4())}],
        "agent_run_id": str(uuid4()),
        "assessed_at": "2026-08-30T10:00:00Z",
    }


def valid_recommendation_payload() -> dict[str, object]:
    return {
        "recommendation_id": str(uuid4()),
        "user_id": str(uuid4()),
        **versioned_input_references(),
        "assessment_ids": [str(uuid4()), str(uuid4())],
        "final_score": 82,
        "rank": 1,
        "classification": "PRIORITY",
        "explanation": "Strong fit for engineering leadership and career direction.",
        "ranking_version": "1.0",
        "created_at": "2026-08-30T10:00:00Z",
    }


def valid_feedback_payload() -> dict[str, object]:
    return {
        "feedback_id": str(uuid4()),
        "user_id": str(uuid4()),
        "job_id": str(uuid4()),
        "action": "INTERESTED",
        "reason": "Relevant leadership scope",
        "created_at": "2026-08-30T10:00:00Z",
    }


def test_assessment_records_exact_versioned_inputs() -> None:
    assessment = Assessment.model_validate(valid_assessment_payload())

    assert assessment.assessment_type is AssessmentType.FIT
    assert assessment.score == 82
    assert assessment.job_profile_revision == 3


@pytest.mark.parametrize("score", [-1, 101])
def test_assessment_rejects_scores_outside_the_agreed_scale(score: int) -> None:
    with pytest.raises(ValidationError):
        Assessment.model_validate({**valid_assessment_payload(), "score": score})


@pytest.mark.parametrize("revision_field", ["candidate_profile_revision", "job_profile_revision"])
def test_assessment_requires_versioned_inputs(revision_field: str) -> None:
    with pytest.raises(ValidationError):
        Assessment.model_validate({**valid_assessment_payload(), revision_field: 0})


def test_recommendation_round_trips_with_its_exact_inputs() -> None:
    recommendation = Recommendation.model_validate(valid_recommendation_payload())

    restored = Recommendation.model_validate_json(recommendation.model_dump_json())

    assert restored.classification is RecommendationClassification.PRIORITY
    assert len(restored.assessment_ids) == 2


@pytest.mark.parametrize("classification", RecommendationClassification)
def test_recommendation_supports_the_approved_classifications(
    classification: RecommendationClassification,
) -> None:
    recommendation = Recommendation.model_validate(
        {**valid_recommendation_payload(), "classification": classification}
    )

    assert recommendation.classification is classification


def test_recommendation_rejects_missing_assessments_and_invalid_rank() -> None:
    with pytest.raises(ValidationError):
        Recommendation.model_validate({**valid_recommendation_payload(), "assessment_ids": []})

    with pytest.raises(ValidationError):
        Recommendation.model_validate({**valid_recommendation_payload(), "rank": 0})


@pytest.mark.parametrize("action", FeedbackAction)
def test_feedback_supports_only_the_documented_actions(action: FeedbackAction) -> None:
    feedback = UserFeedback.model_validate({**valid_feedback_payload(), "action": action})

    assert feedback.action is action


def test_user_decision_contracts_require_user_ownership() -> None:
    for contract, payload in (
        (Assessment, valid_assessment_payload()),
        (Recommendation, valid_recommendation_payload()),
        (UserFeedback, valid_feedback_payload()),
    ):
        payload.pop("user_id")
        with pytest.raises(ValidationError):
            contract.model_validate(payload)
