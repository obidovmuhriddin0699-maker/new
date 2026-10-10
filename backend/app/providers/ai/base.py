"""Provider-agnostic AI interface. Agents depend on this, never on a concrete vendor."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


class AIProviderError(Exception):
    """Base error. ``code`` is stable and ``message`` is safe to show to the user."""

    code = "ai_provider_error"
    category = "provider_error"

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class AIProviderUnavailableError(AIProviderError):
    code = "ai_provider_unavailable"
    category = "provider_unavailable"


class AIModelNotFoundError(AIProviderError):
    code = "ai_model_not_found"
    category = "model_not_found"


class AIProviderTimeoutError(AIProviderError):
    code = "ai_provider_timeout"
    category = "timeout"


class AIInvalidResponseError(AIProviderError):
    """The provider answered, but not with a usable response (bad JSON envelope, empty, huge)."""

    code = "ai_invalid_response"
    category = "invalid_response"


class AIOutputValidationError(AIProviderError):
    """The model's output did not match the required structured schema."""

    code = "ai_invalid_output"
    category = "invalid_output"

    def __init__(self, message: str, *, errors: list[str] | None = None) -> None:
        super().__init__(message)
        self.errors = errors or []


@dataclass(slots=True)
class AIResponse:
    text: str
    model: str
    provider: str
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ProviderStatus:
    provider: str
    model: str
    available: bool
    model_installed: bool
    error_code: str | None = None
    message: str | None = None


class AIProvider(ABC):
    """Interface every LLM backend implements (Ollama, OpenAI-compatible, Claude-compatible...).

    Only ``generate_text`` and ``health`` are required. Structured generation,
    validation and retries live in the agent layer, so they behave the same for
    every provider.
    """

    name: str
    model: str

    @abstractmethod
    async def generate_text(
        self,
        prompt: str,
        *,
        system: str | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        json_mode: bool = False,
    ) -> AIResponse: ...

    @abstractmethod
    async def health(self) -> ProviderStatus: ...

    async def aclose(self) -> None:  # pragma: no cover - default no-op
        return None
