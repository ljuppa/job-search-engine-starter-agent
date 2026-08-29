from typing import Any, Protocol, TypeVar
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class LLMProvider(Protocol):
    async def generate_structured(
        self,
        *,
        messages: list[dict[str, str]],
        response_model: type[T],
        model: str,
        metadata: dict[str, Any] | None = None,
    ) -> T: ...


class LLMGateway:
    """Provider-neutral LLM boundary.

    OpenAI is the first adapter, but agents should depend only on this contract.
    Routing, telemetry, retries and provider capabilities will be implemented here.
    """

    def __init__(self, providers: dict[str, LLMProvider]) -> None:
        self._providers = providers

    async def generate_structured(
        self,
        *,
        provider: str,
        model: str,
        messages: list[dict[str, str]],
        response_model: type[T],
        metadata: dict[str, Any] | None = None,
    ) -> T:
        return await self._providers[provider].generate_structured(
            messages=messages,
            response_model=response_model,
            model=model,
            metadata=metadata,
        )
