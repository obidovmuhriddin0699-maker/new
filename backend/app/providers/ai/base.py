"""Provider-agnostic AI interface. Agents depend on this, never on a concrete vendor."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


class AIProviderError(Exception):
    """Base error. ``code`` is stable and safe to show to the user."""

    code = "ai_provider_error"

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class AIProviderUnavailableError(AIProviderError):
    code = "ai_provider_unavailable"


class AIModelNotFoundError(AIProviderError):
    code = "ai_model_not_found"


class AIProviderTimeoutError(AIProviderError):
    code = "ai_provider_timeout"


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

    Higher-level methods (content plan, caption, reels script, analysis) are built
    on ``generate_text`` by the agent layer in PHASE 3, so a new provider only
    needs ``generate_text`` and ``health``.
    """

    name: str

    @abstractmethod
    async def generate_text(
        self,
        prompt: str,
        *,
        system: str | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
    ) -> AIResponse: ...

    @abstractmethod
    async def health(self) -> ProviderStatus: ...

    async def aclose(self) -> None:  # pragma: no cover - default no-op
        return None
