"""Version-controlled model registry and capability routing."""

from collections.abc import Iterable

from pydantic import BaseModel, ConfigDict, Field

from .contracts import CapabilityUnavailableError, LLMRequest, ModelCapability, ModelNotFoundError


class ModelDefinition(BaseModel):
    """A logical model's provider route and verified capabilities."""

    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)

    key: str = Field(min_length=1)
    provider: str = Field(min_length=1)
    provider_model: str = Field(min_length=1)
    capabilities: frozenset[ModelCapability] = Field(default_factory=frozenset)


class ModelRegistry:
    """In-code registry that prevents agents from choosing raw provider models."""

    def __init__(self, definitions: Iterable[ModelDefinition]) -> None:
        self._definitions: dict[str, ModelDefinition] = {}
        for definition in definitions:
            if definition.key in self._definitions:
                raise ValueError(f"duplicate model key: {definition.key}")
            self._definitions[definition.key] = definition

    def resolve(self, request: LLMRequest) -> ModelDefinition:
        try:
            definition = self._definitions[request.model_key]
        except KeyError as error:
            raise ModelNotFoundError(f"unknown model key: {request.model_key}") from error

        missing_capabilities = request.required_capabilities - definition.capabilities
        if missing_capabilities:
            missing = ", ".join(sorted(capability.value for capability in missing_capabilities))
            raise CapabilityUnavailableError(
                f"model key {request.model_key} lacks required capabilities: {missing}"
            )
        return definition
