from uuid import uuid4

import pytest

from src.agents.profiler.contracts import ProfilerInput, ProfilerResult, ProfilerSource
from src.agents.profiler.extraction import LLMGatewayProfilerExtractor
from src.domain.contracts import ExecutionContext, ExecutionScope
from src.llm.contracts import LLMResponse, LLMUsage


class FakeGateway:
    def __init__(self) -> None:
        self.request = None

    async def generate_structured(self, *, request, response_model):
        self.request = request
        return LLMResponse(request_id=request.request_id, provider="fake", provider_model="fake-1", output=response_model(), usage=LLMUsage(), latency_ms=1)


@pytest.mark.asyncio
async def test_profiler_extraction_uses_only_the_gateway_and_structured_output() -> None:
    gateway = FakeGateway()
    extractor = LLMGatewayProfilerExtractor(gateway)  # type: ignore[arg-type]
    profiler_input = ProfilerInput(
        context=ExecutionContext(correlation_id=uuid4(), trace_id=uuid4(), workflow_run_id=uuid4(), scope=ExecutionScope.USER, user_id=uuid4()),
        sources=[ProfilerSource(source_id=uuid4(), source_type="CV", source_reference="cv.pdf", content="Experience")],
        prompt_version="profiler.extract.v1",
    )

    result = await extractor.extract(profiler_input)

    assert result == ProfilerResult()
    assert gateway.request.model_key == "openai-structured-default"
    assert gateway.request.required_capabilities == {"STRUCTURED_OUTPUT"}
