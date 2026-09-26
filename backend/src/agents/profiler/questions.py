"""Deterministic questions needed before a profile can be confirmed."""

from src.domain.contracts import CandidateProfile

from .contracts import ProfilerQuestion, ProfilerQuestionKind, ProfilerQuestionTopic


def missing_hard_constraint_questions(profile: CandidateProfile) -> list[ProfilerQuestion]:
    questions: list[ProfilerQuestion] = []
    if not profile.target_roles:
        questions.append(ProfilerQuestion(topic=ProfilerQuestionTopic.TARGET_ROLES, kind=ProfilerQuestionKind.MULTI_SELECT, text="Which roles are you targeting?", required_for_confirmation=True))
    if not profile.location_preferences.preferred_locations:
        questions.append(ProfilerQuestion(topic=ProfilerQuestionTopic.PREFERRED_LOCATIONS, kind=ProfilerQuestionKind.FREE_TEXT, text="Which locations are acceptable to you?", required_for_confirmation=True))
    if not profile.work_model_preferences.acceptable_models:
        questions.append(ProfilerQuestion(topic=ProfilerQuestionTopic.WORK_MODEL, kind=ProfilerQuestionKind.MULTI_SELECT, text="Which work models are acceptable to you?", required_for_confirmation=True))
    return questions
