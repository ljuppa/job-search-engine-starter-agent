"""Provider-neutral LLM gateway contracts and routing."""

from .contracts import (
    CapabilityUnavailableError,
    LLMGatewayError,
    LLMMessage,
    LLMRequest,
    LLMResponse,
    LLMUsage,
    MessageRole,
    ModelCapability,
    ModelNotFoundError,
    ProviderRequestError,
    ProviderUnavailableError,
    RateLimitedError,
    StructuredOutputError,
)
from .gateway import LLMGateway, LLMProvider
from .policy import RetryPolicy
from .registry import ModelDefinition, ModelRegistry, default_model_registry
from .telemetry import LLMTelemetryEvent, LLMTelemetrySink, TelemetryOutcome

__all__ = [
    "CapabilityUnavailableError",
    "LLMGateway",
    "LLMGatewayError",
    "LLMMessage",
    "LLMProvider",
    "LLMRequest",
    "LLMResponse",
    "LLMTelemetryEvent",
    "LLMTelemetrySink",
    "LLMUsage",
    "MessageRole",
    "ModelCapability",
    "ModelDefinition",
    "ModelNotFoundError",
    "ModelRegistry",
    "ProviderRequestError",
    "ProviderUnavailableError",
    "RateLimitedError",
    "RetryPolicy",
    "StructuredOutputError",
    "TelemetryOutcome",
    "default_model_registry",
]
