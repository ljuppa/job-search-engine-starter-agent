import asyncio
from collections.abc import Awaitable, Callable

import pytest
from pydantic import BaseModel

from src.llm import (
    LLMGateway,
    LLMMessage,
    LLMRequest,
    LLMResponse,
    LLMUsage,
    MessageRole,
    ModelCapability,
    ModelDefinition,
    ModelRegistry,
    ProviderRequestError,
    ProviderUnavailableError,
    RateLimitedError,
    RetryPolicy,
    TelemetryOutcome,
)
from src.llm.telemetry import LLMTelemetryEvent


class Extraction(BaseModel):
    summary: str


def request_for() -> LLMRequest:
    return LLMRequest(
        request_id="11111111-1111-4111-8111-111111111111",
        model_key="structured-default",
        messages=[LLMMessage(role=MessageRole.USER, content="Extract the summary.")],
        required_capabilities={ModelCapability.STRUCTURED_OUTPUT},
    )


def model_registry() -> ModelRegistry:
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


def successful_response(request: LLMRequest) -> LLMResponse[Extraction]:
    return LLMResponse(
        request_id=request.request_id,
        provider="fake",
        provider_model="fake-structured-1",
        output=Extraction(summary="Structured result"),
        usage=LLMUsage(input_tokens=10, output_tokens=4, total_tokens=14),
        latency_ms=42,
    )


class SequencedProvider:
    def __init__(self, outcomes: list[LLMResponse[Extraction] | Exception]) -> None:
        self._outcomes = outcomes
        self.calls = 0

    async def generate_structured(
        self,
        *,
        request: LLMRequest,
        response_model: type[Extraction],
        model: ModelDefinition,
    ) -> LLMResponse[Extraction]:
        self.calls += 1
        outcome = self._outcomes.pop(0)
        if isinstance(outcome, Exception):
            raise outcome
        return outcome


class RecordingSink:
    def __init__(self) -> None:
        self.events: list[LLMTelemetryEvent] = []

    async def emit(self, event: LLMTelemetryEvent) -> None:
        self.events.append(event)


class FailingSink:
    async def emit(self, event: LLMTelemetryEvent) -> None:
        raise RuntimeError("telemetry is unavailable")


def gateway_for(
    provider: SequencedProvider,
    *,
    retry_policy: RetryPolicy | None = None,
    sink: RecordingSink | FailingSink | None = None,
    sleep: Callable[[float], Awaitable[None]] = asyncio.sleep,
) -> LLMGateway:
    return LLMGateway(
        registry=model_registry(),
        providers={"fake": provider},
        retry_policy=retry_policy or RetryPolicy(),
        telemetry_sink=sink,
        sleep=sleep,
        jitter=lambda _low, _high: 0,
    )


@pytest.mark.asyncio
async def test_gateway_retries_retryable_failure_and_emits_one_success_event() -> None:
    request = request_for()
    provider = SequencedProvider([RateLimitedError("slow down"), successful_response(request)])
    sink = RecordingSink()
    delays: list[float] = []

    async def record_sleep(delay: float) -> None:
        delays.append(delay)

    response = await gateway_for(provider, sink=sink, sleep=record_sleep).generate_structured(
        request=request, response_model=Extraction
    )

    assert response.output.summary == "Structured result"
    assert provider.calls == 2
    assert delays == [0.25]
    assert len(sink.events) == 1
    assert sink.events[0].outcome is TelemetryOutcome.SUCCESS
    assert sink.events[0].attempts == 2
    assert sink.events[0].usage == response.usage


@pytest.mark.asyncio
async def test_gateway_does_not_retry_non_retryable_failure() -> None:
    provider = SequencedProvider([ProviderRequestError("invalid request")])
    sink = RecordingSink()
    delays: list[float] = []

    async def record_sleep(delay: float) -> None:
        delays.append(delay)

    with pytest.raises(ProviderRequestError):
        await gateway_for(provider, sink=sink, sleep=record_sleep).generate_structured(
            request=request_for(), response_model=Extraction
        )

    assert provider.calls == 1
    assert delays == []
    assert sink.events[0].outcome is TelemetryOutcome.FAILURE
    assert sink.events[0].attempts == 1
    assert sink.events[0].error_code == "PROVIDER_REQUEST_ERROR"


@pytest.mark.asyncio
async def test_gateway_maps_timeout_to_retryable_provider_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    provider = SequencedProvider([successful_response(request_for())])
    sink = RecordingSink()

    async def immediately_timeout(awaitable: Awaitable[object], *, timeout: float) -> object:
        close = getattr(awaitable, "close", None)
        if close is not None:
            close()
        raise TimeoutError

    monkeypatch.setattr("src.llm.gateway.asyncio.wait_for", immediately_timeout)

    with pytest.raises(ProviderUnavailableError, match="timed out") as error:
        await gateway_for(
            provider,
            retry_policy=RetryPolicy(max_attempts=1),
            sink=sink,
        ).generate_structured(request=request_for(), response_model=Extraction)

    assert error.value.retryable is True
    assert provider.calls == 0
    assert sink.events[0].error_code == "PROVIDER_UNAVAILABLE"


@pytest.mark.asyncio
async def test_gateway_does_not_fail_when_telemetry_sink_fails() -> None:
    request = request_for()
    provider = SequencedProvider([successful_response(request)])

    response = await gateway_for(provider, sink=FailingSink()).generate_structured(
        request=request, response_model=Extraction
    )

    assert response.output.summary == "Structured result"


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"max_attempts": 0}, "max_attempts"),
        ({"timeout_seconds": 0}, "timeout_seconds"),
        ({"initial_backoff_seconds": -1}, "initial_backoff_seconds"),
        ({"initial_backoff_seconds": 1, "max_backoff_seconds": 0.5}, "max_backoff_seconds"),
    ],
)
def test_retry_policy_rejects_invalid_values(kwargs: dict[str, float | int], message: str) -> None:
    with pytest.raises(ValueError, match=message):
        RetryPolicy(**kwargs)
