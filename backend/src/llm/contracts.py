"""Provider-neutral contracts for structured LLM requests and responses."""

from enum import Enum
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, JsonValue

type NonEmptyText = Annotated[str, Field(min_length=1)]
type NonNegativeInt = Annotated[int, Field(ge=0)]

class MessageRole(str, Enum):
    SYSTEM = "SYSTEM"
    USER = "USER"
    ASSISTANT = "ASSISTANT"


class ModelCapability(str, Enum):
    STRUCTURED_OUTPUT = "STRUCTURED_OUTPUT"


class LLMMessage(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    role: MessageRole
    content: NonEmptyText


class LLMRequest(BaseModel):
    """A request addressed to a registered logical model, never a provider SDK."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    request_id: UUID
    model_key: NonEmptyText
    messages: list[LLMMessage] = Field(min_length=1)
    required_capabilities: set[ModelCapability] = Field(default_factory=set)
    prompt_version: NonEmptyText | None = None
    metadata: dict[NonEmptyText, JsonValue] = Field(default_factory=dict)


class LLMUsage(BaseModel):
    model_config = ConfigDict(extra="forbid")

    input_tokens: NonNegativeInt | None = None
    output_tokens: NonNegativeInt | None = None
    total_tokens: NonNegativeInt | None = None


class LLMResponse[T: BaseModel](BaseModel):
    """Normalised successful provider result and its operational telemetry."""

    model_config = ConfigDict(extra="forbid")

    request_id: UUID
    provider: NonEmptyText
    provider_model: NonEmptyText
    output: T
    usage: LLMUsage = Field(default_factory=LLMUsage)
    latency_ms: NonNegativeInt


class LLMGatewayError(Exception):
    """Base class for failures normalised at the gateway boundary."""

    code = "LLM_GATEWAY_ERROR"
    retryable = False


class ModelNotFoundError(LLMGatewayError):
    code = "MODEL_NOT_FOUND"


class CapabilityUnavailableError(LLMGatewayError):
    code = "CAPABILITY_UNAVAILABLE"


class ProviderUnavailableError(LLMGatewayError):
    code = "PROVIDER_UNAVAILABLE"
    retryable = True


class RateLimitedError(LLMGatewayError):
    code = "RATE_LIMITED"
    retryable = True


class StructuredOutputError(LLMGatewayError):
    code = "STRUCTURED_OUTPUT_ERROR"
