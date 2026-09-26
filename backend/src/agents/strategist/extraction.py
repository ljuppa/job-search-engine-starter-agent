"""Gateway-backed strategic-signal extraction."""

import json
from uuid import uuid4

from src.llm.contracts import LLMMessage, LLMRequest, MessageRole, ModelCapability
from src.llm.gateway import LLMGateway

from .contracts import StrategistDraft, StrategistInput


class LLMGatewayStrategistExtractor:
    def __init__(self, gateway: LLMGateway, model_key: str = "openai-structured-default") -> None:
        self._gateway = gateway
        self._model_key = model_key

    async def extract(self, strategist_input: StrategistInput) -> StrategistDraft:
        payload = {"candidate_profile": strategist_input.candidate_profile.model_dump(mode="json"), "job_profile": strategist_input.job_profile.model_dump(mode="json")}
        request = LLMRequest(request_id=uuid4(), model_key=self._model_key, required_capabilities={ModelCapability.STRUCTURED_OUTPUT}, prompt_version=strategist_input.prompt_version, messages=[LLMMessage(role=MessageRole.SYSTEM, content="Extract only evidence-grounded career opportunities, risks, and uncertainties. Do not score the job or invent market optionality."), LLMMessage(role=MessageRole.USER, content=json.dumps(payload))], metadata={"agent": "strategist", "schema_version": strategist_input.schema_version})
        return (await self._gateway.generate_structured(request=request, response_model=StrategistDraft)).output
