"""LLM Gateway-backed structured Profiler extraction."""

import json
from uuid import uuid4

from src.llm.contracts import LLMMessage, LLMRequest, MessageRole, ModelCapability
from src.llm.gateway import LLMGateway

from .contracts import ProfilerInput, ProfilerResult


class LLMGatewayProfilerExtractor:
    """Adapter which keeps provider SDKs outside the Profiler package."""

    def __init__(self, gateway: LLMGateway, model_key: str = "openai-structured-default") -> None:
        self._gateway = gateway
        self._model_key = model_key

    async def extract(self, profiler_input: ProfilerInput) -> ProfilerResult:
        payload = {
            "sources": [source.model_dump(mode="json") for source in profiler_input.sources],
            "current_profile": profiler_input.current_profile.model_dump(mode="json") if profiler_input.current_profile else None,
        }
        request = LLMRequest(
            request_id=uuid4(), model_key=self._model_key,
            required_capabilities={ModelCapability.STRUCTURED_OUTPUT}, prompt_version=profiler_input.prompt_version,
            messages=[
                LLMMessage(role=MessageRole.SYSTEM, content="Extract only evidence-grounded candidate profile facts. Return ProfileResult. Do not invent information."),
                LLMMessage(role=MessageRole.USER, content=json.dumps(payload)),
            ],
            metadata={"agent": "profiler", "schema_version": profiler_input.schema_version},
        )
        response = await self._gateway.generate_structured(request=request, response_model=ProfilerResult)
        return response.output
