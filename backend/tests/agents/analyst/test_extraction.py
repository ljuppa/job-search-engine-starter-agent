from datetime import UTC, datetime
from uuid import uuid4

import pytest

from src.agents.analyst import AnalystInput
from src.agents.analyst.extraction import LLMGatewayAnalystExtractor
from src.domain.contracts import ExecutionContext, ExecutionScope, Job, RawJob
from src.llm.contracts import LLMResponse, LLMUsage


class FakeGateway:
    async def generate_structured(self, *, request, response_model):
        self.request = request
        return LLMResponse(request_id=request.request_id, provider="fake", provider_model="fake", output=response_model(profile_draft={}), usage=LLMUsage(), latency_ms=1)


def analyst_input() -> AnalystInput:
    raw = RawJob(raw_job_id=uuid4(), source_name="test", external_id="123", source_url="https://example.com/jobs/123", retrieved_at=datetime.now(UTC), title="Engineer", company_name="Example", description="Role description", source_payload={}, content_hash="abc")
    job = Job(job_id=uuid4(), canonical_key="example-engineer", raw_job_ids=[raw.raw_job_id], created_at=datetime.now(UTC), updated_at=datetime.now(UTC))
    return AnalystInput(context=ExecutionContext(correlation_id=uuid4(), trace_id=uuid4(), workflow_run_id=uuid4(), scope=ExecutionScope.GLOBAL), raw_job=raw, job=job, prompt_version="analyst.extract.v1")


@pytest.mark.asyncio
async def test_analyst_extraction_uses_gateway_structured_output() -> None:
    gateway = FakeGateway()
    await LLMGatewayAnalystExtractor(gateway).extract(analyst_input())  # type: ignore[arg-type]

    assert gateway.request.metadata["agent"] == "analyst"
    assert gateway.request.required_capabilities == {"STRUCTURED_OUTPUT"}
