"""Gateway-backed structured extraction for the Analyst module."""

import json
from uuid import uuid4

from src.llm.contracts import LLMMessage, LLMRequest, MessageRole, ModelCapability
from src.llm.gateway import LLMGateway

from .contracts import AnalystInput, AnalystResult


class LLMGatewayAnalystExtractor:
    def __init__(self, gateway: LLMGateway, model_key: str = "openai-structured-default") -> None:
        self._gateway = gateway
        self._model_key = model_key

    async def extract(self, analyst_input: AnalystInput) -> AnalystResult:
        request = LLMRequest(
            request_id=uuid4(), model_key=self._model_key,
            required_capabilities={ModelCapability.STRUCTURED_OUTPUT}, prompt_version=analyst_input.prompt_version,
            messages=[
                LLMMessage(role=MessageRole.SYSTEM, content="Normalize only facts stated in this job posting. Mark unavailable data as unknown. Do not invent compensation, location, seniority, or requirements."),
                LLMMessage(role=MessageRole.USER, content=json.dumps(analyst_input.raw_job.model_dump(mode="json"))),
            ],
            metadata={"agent": "analyst", "schema_version": analyst_input.schema_version},
        )
        response = await self._gateway.generate_structured(request=request, response_model=AnalystResult)
        return response.output
