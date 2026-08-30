"""OpenAI Responses API adapter behind the provider-neutral gateway."""

from time import perf_counter
from typing import Any, TypeVar

from openai import APIConnectionError, APIStatusError, APITimeoutError, AsyncOpenAI, RateLimitError
from pydantic import BaseModel, ValidationError

from ..contracts import (
    LLMMessage,
    LLMRequest,
    LLMResponse,
    LLMUsage,
    MessageRole,
    ProviderRequestError,
    ProviderUnavailableError,
    RateLimitedError,
    StructuredOutputError,
)
from ..registry import ModelDefinition

T = TypeVar("T", bound=BaseModel)


class OpenAIProvider:
    """Translates canonical structured requests to the OpenAI Responses API."""

    def __init__(self, client: Any) -> None:
        self._client = client

    @classmethod
    def from_api_key(cls, api_key: str) -> "OpenAIProvider":
        return cls(AsyncOpenAI(api_key=api_key))

    async def generate_structured(
        self,
        *,
        request: LLMRequest,
        response_model: type[T],
        model: ModelDefinition,
    ) -> LLMResponse[T]:
        instructions, input_messages = self._map_messages(request.messages)
        metadata = self._validate_metadata(request.metadata)
        started_at = perf_counter()
        try:
            response = await self._client.responses.create(
                model=model.provider_model,
                instructions=instructions or None,
                input=input_messages,
                metadata=metadata,
                store=False,
                text={
                    "format": {
                        "type": "json_schema",
                        "name": response_model.__name__,
                        "schema": response_model.model_json_schema(),
                        "strict": True,
                    }
                },
            )
        except RateLimitError as error:
            raise RateLimitedError(str(error)) from error
        except (APIConnectionError, APITimeoutError) as error:
            raise ProviderUnavailableError(str(error)) from error
        except APIStatusError as error:
            if error.status_code >= 500:
                raise ProviderUnavailableError(str(error)) from error
            raise ProviderRequestError(str(error)) from error

        try:
            if response.status != "completed":
                raise ValueError(f"OpenAI response status was {response.status}")
            output = response_model.model_validate_json(response.output_text)
        except (ValidationError, ValueError, TypeError) as error:
            raise StructuredOutputError(str(error)) from error

        usage = getattr(response, "usage", None)
        return LLMResponse(
            request_id=request.request_id,
            provider=model.provider,
            provider_model=model.provider_model,
            output=output,
            usage=LLMUsage(
                input_tokens=getattr(usage, "input_tokens", None),
                output_tokens=getattr(usage, "output_tokens", None),
                total_tokens=getattr(usage, "total_tokens", None),
            ),
            latency_ms=round((perf_counter() - started_at) * 1000),
        )

    @staticmethod
    def _map_messages(messages: list[LLMMessage]) -> tuple[str, list[dict[str, str]]]:
        instructions = "\n\n".join(
            message.content for message in messages if message.role is MessageRole.SYSTEM
        )
        input_messages = [
            {"role": message.role.value.lower(), "content": message.content}
            for message in messages
            if message.role is not MessageRole.SYSTEM
        ]
        return instructions, input_messages

    @staticmethod
    def _validate_metadata(metadata: dict[str, object]) -> dict[str, str]:
        if any(not isinstance(value, str) for value in metadata.values()):
            raise ProviderRequestError("OpenAI metadata values must be strings")
        return dict(metadata)
