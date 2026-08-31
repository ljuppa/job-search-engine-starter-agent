import pytest
from pydantic import BaseModel

from src.llm import (
    CapabilityUnavailableError,
    LLMGateway,
    LLMMessage,
    LLMRequest,
    LLMResponse,
    LLMUsage,
    MessageRole,
    ModelCapability,
    ModelDefinition,
    ModelNotFoundError,
    ModelRegistry,
    ProviderUnavailableError,
)


class Extraction(BaseModel):
    summary: str


def request_for(model_key: str = "structured-default") -> LLMRequest:
    return LLMRequest(
        request_id="11111111-1111-4111-8111-111111111111",
        model_key=model_key,
        messages=[LLMMessage(role=MessageRole.USER, content="Extract the summary.")],
        required_capabilities={ModelCapability.STRUCTURED_OUTPUT},
        prompt_version="profiler.extract.v1",
    )


def registry() -> ModelRegistry:
    return ModelRegistry(
        [
            ModelDefinition(
                key="structured-default",
                provider="fake",
                provider_model="fake-structured-1",
                capabilities=frozenset({ModelCapability.STRUCTURED_OUTPUT}),
            )
        ]
    )


class FakeProvider:
    async def generate_structured(
        self,
        *,
        request: LLMRequest,
        response_model: type[Extraction],
        model: ModelDefinition,
    ) -> LLMResponse[Extraction]:
        return LLMResponse(
            request_id=request.request_id,
            provider=model.provider,
            provider_model=model.provider_model,
            output=response_model(summary="Structured result"),
            usage=LLMUsage(input_tokens=10, output_tokens=4, total_tokens=14),
            latency_ms=42,
        )


def test_registry_resolves_a_capability_compatible_model() -> None:
    resolved = registry().resolve(request_for())

    assert resolved.provider == "fake"
    assert resolved.provider_model == "fake-structured-1"


def test_registry_rejects_unknown_model_key() -> None:
    with pytest.raises(ModelNotFoundError):
        registry().resolve(request_for("unknown"))


def test_registry_rejects_missing_capabilities() -> None:
    incompatible_registry = ModelRegistry(
        [ModelDefinition(key="plain", provider="fake", provider_model="fake-plain-1")]
    )

    with pytest.raises(CapabilityUnavailableError):
        incompatible_registry.resolve(request_for("plain"))


def test_registry_rejects_duplicate_model_keys() -> None:
    definition = ModelDefinition(key="duplicate", provider="fake", provider_model="fake-1")

    with pytest.raises(ValueError, match="duplicate model key"):
        ModelRegistry([definition, definition])


@pytest.mark.asyncio
async def test_gateway_returns_normalised_structured_response_and_usage() -> None:
    gateway = LLMGateway(registry=registry(), providers={"fake": FakeProvider()})

    response = await gateway.generate_structured(request=request_for(), response_model=Extraction)

    assert response.output.summary == "Structured result"
    assert response.usage.total_tokens == 14
    assert response.latency_ms == 42


@pytest.mark.asyncio
async def test_gateway_raises_typed_error_for_an_unconfigured_provider() -> None:
    gateway = LLMGateway(registry=registry(), providers={})

    with pytest.raises(ProviderUnavailableError) as error:
        await gateway.generate_structured(request=request_for(), response_model=Extraction)

    assert error.value.retryable is True
