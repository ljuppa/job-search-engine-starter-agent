from uuid import UUID, uuid4

from src.agents.profiler.questions import missing_hard_constraint_questions
from src.domain.contracts import CandidateProfile, ProfileStatus, WorkModel, WorkModelPreferences


def test_questions_cover_only_missing_confirmation_constraints() -> None:
    profile = CandidateProfile(
        user_id=UUID("11111111-1111-4111-8111-111111111111"), profile_id=uuid4(), revision=1,
        profile_status=ProfileStatus.DRAFT, target_roles=["Engineering Manager"],
        work_model_preferences=WorkModelPreferences(acceptable_models=[WorkModel.REMOTE]),
    )

    questions = missing_hard_constraint_questions(profile)

    assert [question.topic.value for question in questions] == ["PREFERRED_LOCATIONS"]
