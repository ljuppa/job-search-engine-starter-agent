from uuid import uuid4

from src.agents.matcher.policy import calculate_score, evaluate_constraints
from src.domain.contracts import (
    CandidateProfile,
    JobProfile,
    ProfileStatus,
    WorkModel,
    WorkModelPreferences,
)


def test_structured_constraint_failure_overrides_fit_score() -> None:
    profile = CandidateProfile(user_id=uuid4(), profile_id=uuid4(), revision=1, profile_status=ProfileStatus.CONFIRMED, work_model_preferences=WorkModelPreferences(acceptable_models=[WorkModel.REMOTE]))
    job = JobProfile(job_profile_id=uuid4(), job_id=uuid4(), revision=1, analysed_at="2026-09-26T00:00:00Z", work_model=WorkModel.ONSITE)

    result = evaluate_constraints(profile, job)

    assert result.eligible is False
    assert calculate_score(constraints=result, strengths=5, gaps=0, risks=0) == 0


def test_free_text_hard_constraints_are_visible_but_not_automatic_filters() -> None:
    profile = CandidateProfile(user_id=uuid4(), profile_id=uuid4(), revision=1, profile_status=ProfileStatus.CONFIRMED, hard_constraints=["No defence sector roles"])
    job = JobProfile(job_profile_id=uuid4(), job_id=uuid4(), revision=1, analysed_at="2026-09-26T00:00:00Z")

    result = evaluate_constraints(profile, job)

    assert result.eligible is True
    assert "free-text hard constraints require explicit review" in result.unknowns
