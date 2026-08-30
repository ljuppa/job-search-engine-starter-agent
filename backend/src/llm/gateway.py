from typing import Protocol, TypeVar

from pydantic import BaseModel

from .contracts import LLMRequest, LLMResponse, ProviderUnavailableError
from .registry import ModelDefinition, ModelRegistry

T = TypeVar("T", bound=BaseModel)


class LLMProvider(Protocol):
    async def generate_structured(
        self,
        *,
        request: LLMRequest,
        response_model: type[T],
        model: ModelDefinition,
    ) -> LLMResponse[T]: ...


class LLMGateway:
    """Provider-neutral LLM boundary.

    OpenAI is the first adapter, but agents should depend only on this contract.
    Routing, telemetry, retries and provider capabilities will be implemented here.
    """

    def __init__(self, *, registry: ModelRegistry, providers: dict[str, LLMProvider]) -> None:
        self._registry = registry
        self._providers = providers

    async def generate_structured(
        self,
        *,
        request: LLMRequest,
        response_model: type[T],
    ) -> LLMResponse[T]:
        model = self._registry.resolve(request)
        provider = self._providers.get(model.provider)
        if provider is None:
            raise ProviderUnavailableError(f"provider is not configured: {model.provider}")
        return await provider.generate_structured(
            request=request,
            response_model=response_model,
            model=model,
        )
