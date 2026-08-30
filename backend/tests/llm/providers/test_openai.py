from types import SimpleNamespace

import pytest
from pydantic import BaseModel

from src.llm import (
    LLMMessage,
    LLMRequest,
    MessageRole,
    ModelCapability,
    ModelDefinition,
    ProviderRequestError,
    ProviderUnavailableError,
    RateLimitedError,
    StructuredOutputError,
    default_model_registry,
)
from src.llm.providers import OpenAIProvider
from src.llm.providers import openai as openai_provider_module


class Extraction(BaseModel):
    summary: str


class FakeResponses:
    def __init__(self, response: object) -> None:
        self._response = response
        self.calls: list[dict[str, object]] = []

    async def create(self, **kwargs: object) -> object:
        self.calls.append(kwargs)
        return self._response


class RaisingResponses:
    def __init__(self, error: Exception) -> None:
        self._error = error

    async def create(self, **kwargs: object) -> object:
        raise self._error


def request_for(metadata: dict[str, object] | None = None) -> LLMRequest:
    return LLMRequest(
        request_id="11111111-1111-4111-8111-111111111111",
        model_key="openai-structured-default",
        messages=[
            LLMMessage(role=MessageRole.SYSTEM, content="Extract facts."),
            LLMMessage(role=MessageRole.USER, content="Candidate input."),
        ],
        required_capabilities={ModelCapability.STRUCTURED_OUTPUT},
        metadata=metadata or {"correlation_id": "correlation-1"},
    )


def model_definition() -> ModelDefinition:
    return default_model_registry().resolve(request_for())


def completed_response(output_text: str = '{"summary":"Structured result"}') -> object:
    return SimpleNamespace(
        status="completed",
        output_text=output_text,
        usage=SimpleNamespace(input_tokens=10, output_tokens=4, total_tokens=14),
    )


@pytest.mark.asyncio
async def test_openai_provider_maps_strict_structured_request_and_response() -> None:
    responses = FakeResponses(completed_response())
    provider = OpenAIProvider(SimpleNamespace(responses=responses))

    response = await provider.generate_structured(
        request=request_for(), response_model=Extraction, model=model_definition()
    )

    call = responses.calls[0]
    assert call["model"] == "gpt-5.6-luna"
    assert call["instructions"] == "Extract facts."
    assert call["input"] == [{"role": "user", "content": "Candidate input."}]
    assert call["metadata"] == {"correlation_id": "correlation-1"}
    assert call["store"] is False
    assert call["text"] == {
        "format": {
            "type": "json_schema",
            "name": "Extraction",
            "schema": Extraction.model_json_schema(),
            "strict": True,
        }
    }
    assert response.output.summary == "Structured result"
    assert response.usage.total_tokens == 14


@pytest.mark.asyncio
async def test_openai_provider_rejects_non_string_metadata_before_the_api_call() -> None:
    responses = FakeResponses(completed_response())
    provider = OpenAIProvider(SimpleNamespace(responses=responses))

    with pytest.raises(ProviderRequestError, match="metadata values must be strings"):
        await provider.generate_structured(
            request=request_for({"attempt": 1}), response_model=Extraction, model=model_definition()
        )

    assert responses.calls == []


@pytest.mark.asyncio
async def test_openai_provider_normalises_invalid_structured_output() -> None:
    provider = OpenAIProvider(SimpleNamespace(responses=FakeResponses(completed_response("not json"))))

    with pytest.raises(StructuredOutputError):
        await provider.generate_structured(
            request=request_for(), response_model=Extraction, model=model_definition()
        )


@pytest.mark.asyncio
async def test_openai_provider_normalises_a_rate_limit_error(monkeypatch: pytest.MonkeyPatch) -> None:
    class FakeRateLimitError(Exception):
        pass

    monkeypatch.setattr(openai_provider_module, "RateLimitError", FakeRateLimitError)
    provider = OpenAIProvider(SimpleNamespace(responses=RaisingResponses(FakeRateLimitError())))

    with pytest.raises(RateLimitedError) as error:
        await provider.generate_structured(
            request=request_for(), response_model=Extraction, model=model_definition()
        )

    assert error.value.retryable is True


@pytest.mark.asyncio
async def test_openai_provider_normalises_provider_status_errors(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FakeStatusError(Exception):
        def __init__(self, status_code: int) -> None:
            self.status_code = status_code

    monkeypatch.setattr(openai_provider_module, "APIStatusError", FakeStatusError)

    unavailable_provider = OpenAIProvider(
        SimpleNamespace(responses=RaisingResponses(FakeStatusError(503)))
    )
    with pytest.raises(ProviderUnavailableError):
        await unavailable_provider.generate_structured(
            request=request_for(), response_model=Extraction, model=model_definition()
        )

    invalid_request_provider = OpenAIProvider(
        SimpleNamespace(responses=RaisingResponses(FakeStatusError(400)))
    )
    with pytest.raises(ProviderRequestError):
        await invalid_request_provider.generate_structured(
            request=request_for(), response_model=Extraction, model=model_definition()
        )
