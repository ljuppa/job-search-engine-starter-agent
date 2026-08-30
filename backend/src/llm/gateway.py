import asyncio
from collections.abc import Awaitable, Callable
from random import uniform
from time import perf_counter
from typing import Protocol, TypeVar

from pydantic import BaseModel

from .contracts import LLMGatewayError, LLMRequest, LLMResponse, ProviderUnavailableError
from .policy import RetryPolicy
from .registry import ModelDefinition, ModelRegistry
from .telemetry import LLMTelemetryEvent, LLMTelemetrySink, NoopLLMTelemetrySink, TelemetryOutcome

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

    def __init__(
        self,
        *,
        registry: ModelRegistry,
        providers: dict[str, LLMProvider],
        retry_policy: RetryPolicy | None = None,
        telemetry_sink: LLMTelemetrySink | None = None,
        sleep: Callable[[float], Awaitable[None]] = asyncio.sleep,
        jitter: Callable[[float, float], float] = uniform,
    ) -> None:
        self._registry = registry
        self._providers = providers
        self._retry_policy = retry_policy or RetryPolicy()
        self._telemetry_sink = telemetry_sink or NoopLLMTelemetrySink()
        self._sleep = sleep
        self._jitter = jitter

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
        started_at = perf_counter()
        for attempt in range(1, self._retry_policy.max_attempts + 1):
            try:
                response = await asyncio.wait_for(
                    provider.generate_structured(
                        request=request, response_model=response_model, model=model
                    ),
                    timeout=self._retry_policy.timeout_seconds,
                )
                await self._emit(
                    LLMTelemetryEvent(
                        request_id=request.request_id, model_key=request.model_key,
                        provider=model.provider, provider_model=model.provider_model,
                        attempts=attempt, latency_ms=round((perf_counter() - started_at) * 1000),
                        outcome=TelemetryOutcome.SUCCESS, usage=response.usage,
                    )
                )
                return response
            except TimeoutError as error:
                gateway_error = ProviderUnavailableError("LLM request timed out")
                gateway_error.__cause__ = error
            except LLMGatewayError as error:
                gateway_error = error

            if not gateway_error.retryable or attempt == self._retry_policy.max_attempts:
                await self._emit(
                    LLMTelemetryEvent(
                        request_id=request.request_id, model_key=request.model_key,
                        provider=model.provider, provider_model=model.provider_model,
                        attempts=attempt, latency_ms=round((perf_counter() - started_at) * 1000),
                        outcome=TelemetryOutcome.FAILURE, error_code=gateway_error.code,
                    )
                )
                raise gateway_error

            delay = min(
                self._retry_policy.initial_backoff_seconds * (2 ** (attempt - 1)),
                self._retry_policy.max_backoff_seconds,
            )
            await self._sleep(delay + self._jitter(0, delay))

        raise AssertionError("retry loop must return or raise")

    async def _emit(self, event: LLMTelemetryEvent) -> None:
        try:
            await self._telemetry_sink.emit(event)
        except Exception:  # noqa: BLE001 - telemetry must not affect the LLM result.
            return
