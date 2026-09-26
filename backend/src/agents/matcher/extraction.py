"""Gateway-backed evidence signal extraction for Matcher."""

import json
from uuid import uuid4

from src.llm.contracts import LLMMessage, LLMRequest, MessageRole, ModelCapability
from src.llm.gateway import LLMGateway

from .contracts import MatcherDraft, MatcherInput


class LLMGatewayMatcherExtractor:
    def __init__(self, gateway: LLMGateway, model_key: str = "openai-structured-default") -> None:
        self._gateway = gateway
        self._model_key = model_key

    async def extract(self, matcher_input: MatcherInput) -> MatcherDraft:
        payload = {"candidate_profile": matcher_input.candidate_profile.model_dump(mode="json"), "job_profile": matcher_input.job_profile.model_dump(mode="json")}
        request = LLMRequest(request_id=uuid4(), model_key=self._model_key, required_capabilities={ModelCapability.STRUCTURED_OUTPUT}, prompt_version=matcher_input.prompt_version, messages=[LLMMessage(role=MessageRole.SYSTEM, content="Identify only evidence-grounded current-fit strengths, gaps, and risks. Do not score or decide eligibility."), LLMMessage(role=MessageRole.USER, content=json.dumps(payload))], metadata={"agent": "matcher", "schema_version": matcher_input.schema_version})
        return (await self._gateway.generate_structured(request=request, response_model=MatcherDraft)).output
