from uuid import UUID, uuid4

import pytest
from pydantic import ValidationError

from src.agents.profiler import (
    FactDisposition,
    ProfileChangeDraft,
    ProfileFact,
    ProfilerInput,
    ProfilerQuestion,
    ProfilerQuestionKind,
    ProfilerQuestionOption,
    ProfilerQuestionTopic,
    ProfilerResult,
    ProfilerSource,
)
from src.domain.contracts import (
    CandidateProfile,
    ExecutionContext,
    ExecutionScope,
    ProposalOperation,
)


def user_context(*, profile_id: UUID | None = None, revision: int | None = None) -> ExecutionContext:
    return ExecutionContext(
        correlation_id=uuid4(),
        trace_id=uuid4(),
        workflow_run_id=uuid4(),
        scope=ExecutionScope.USER,
        user_id=UUID("11111111-1111-4111-8111-111111111111"),
        candidate_profile_id=profile_id,
        candidate_profile_revision=revision,
    )


def source() -> ProfilerSource:
    return ProfilerSource(
        source_id=uuid4(),
        source_type="CV",
        source_reference="candidate-cv.pdf",
        content="Engineering leader with software delivery experience.",
    )


def profile() -> CandidateProfile:
    return CandidateProfile(
        user_id="11111111-1111-4111-8111-111111111111",
        profile_id=uuid4(),
        revision=1,
        profile_status="DRAFT",
    )


def test_profiler_input_supports_initial_profile_extraction() -> None:
    profiler_input = ProfilerInput(
        context=user_context(), sources=[source()], prompt_version="profiler.extract.v1"
    )

    assert profiler_input.current_profile is None
    assert profiler_input.context.scope is ExecutionScope.USER


def test_profiler_input_requires_an_exact_current_profile_reference() -> None:
    current_profile = profile()
    profiler_input = ProfilerInput(
        context=user_context(profile_id=current_profile.profile_id, revision=current_profile.revision),
        sources=[source()],
        current_profile=current_profile,
        prompt_version="profiler.extract.v1",
    )

    assert profiler_input.current_profile == current_profile


@pytest.mark.parametrize(
    "context,current_profile",
    [
        (
            ExecutionContext(
                correlation_id=uuid4(),
                trace_id=uuid4(),
                workflow_run_id=uuid4(),
                scope=ExecutionScope.GLOBAL,
            ),
            None,
        ),
        (user_context(profile_id=uuid4(), revision=1), None),
        (user_context(profile_id=uuid4(), revision=1), profile()),
    ],
)
def test_profiler_input_rejects_invalid_profile_scope_or_reference(
    context: ExecutionContext, current_profile: CandidateProfile | None
) -> None:
    with pytest.raises(ValidationError):
        ProfilerInput(
            context=context,
            sources=[source()],
            current_profile=current_profile,
            prompt_version="profiler.extract.v1",
        )


def test_profiler_result_represents_facts_drafts_and_explicit_questions() -> None:
    source_id = uuid4()
    result = ProfilerResult(
        facts=[
            ProfileFact(
                field_path="/capabilities",
                value=["software delivery"],
                disposition=FactDisposition.EXTRACTED,
                confidence=0.9,
                source_ids=[source_id],
            )
        ],
        change_drafts=[
            ProfileChangeDraft(
                operation=ProposalOperation.ADD,
                field_path="/capabilities/-",
                new_value="software delivery",
                rationale="Stated in the supplied CV.",
                confidence=0.9,
                source_ids=[source_id],
            )
        ],
        questions=[
            ProfilerQuestion(
                topic=ProfilerQuestionTopic.WORK_MODEL,
                kind=ProfilerQuestionKind.MULTI_SELECT,
                text="Which work models are acceptable?",
                required_for_confirmation=True,
                options=[
                    ProfilerQuestionOption(key="REMOTE", label="Remote"),
                    ProfilerQuestionOption(key="HYBRID", label="Hybrid"),
                ],
            )
        ],
    )

    assert result.facts[0].disposition is FactDisposition.EXTRACTED
    assert result.change_drafts[0].operation is ProposalOperation.ADD
    assert result.questions[0].required_for_confirmation is True


@pytest.mark.parametrize("type_", [ProfileFact, ProfileChangeDraft])
def test_profiler_profile_paths_must_be_non_root_json_pointers(
    type_: type[ProfileFact] | type[ProfileChangeDraft],
) -> None:
    common = {"field_path": "profile_status"}
    if type_ is ProfileFact:
        payload = {
            **common,
            "value": "CONFIRMED",
            "disposition": "INFERRED",
            "confidence": 0.5,
            "source_ids": [uuid4()],
        }
    else:
        payload = {
            **common,
            "operation": "REPLACE",
            "rationale": "Inference needs confirmation.",
            "confidence": 0.5,
            "source_ids": [uuid4()],
        }

    with pytest.raises(ValidationError):
        type_.model_validate(payload)


def test_profiler_profile_paths_reject_invalid_json_pointer_escapes() -> None:
    with pytest.raises(ValidationError, match="invalid JSON Pointer escape"):
        ProfileFact(
            field_path="/capabilities~2invalid",
            value="software delivery",
            disposition="EXTRACTED",
            confidence=0.9,
            source_ids=[uuid4()],
        )


def test_profiler_question_rejects_duplicate_option_keys() -> None:
    with pytest.raises(ValidationError, match="option keys must be unique"):
        ProfilerQuestion(
            topic="WORK_MODEL",
            kind="MULTI_SELECT",
            text="Which work models are acceptable?",
            required_for_confirmation=True,
            options=[
                ProfilerQuestionOption(key="REMOTE", label="Remote"),
                ProfilerQuestionOption(key="REMOTE", label="Remote only"),
            ],
        )


def test_profiler_result_cannot_carry_a_mutable_candidate_profile() -> None:
    with pytest.raises(ValidationError):
        ProfilerResult.model_validate({"candidate_profile": profile().model_dump(mode="json")})
