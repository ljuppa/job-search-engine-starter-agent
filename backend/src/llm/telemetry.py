"""Typed, provider-neutral LLM telemetry boundary."""

from enum import Enum
from typing import Protocol
from uuid import UUID

from pydantic import BaseModel

from .contracts import LLMUsage


class TelemetryOutcome(str, Enum):
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"


class LLMTelemetryEvent(BaseModel):
    request_id: UUID
    model_key: str
    provider: str | None
    provider_model: str | None
    attempts: int
    latency_ms: int
    outcome: TelemetryOutcome
    usage: LLMUsage | None = None
    error_code: str | None = None


class LLMTelemetrySink(Protocol):
    async def emit(self, event: LLMTelemetryEvent) -> None: ...


class NoopLLMTelemetrySink:
    async def emit(self, event: LLMTelemetryEvent) -> None:
        return None
