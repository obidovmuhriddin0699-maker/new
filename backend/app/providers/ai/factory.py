from app.core.config import Settings, get_settings
from app.providers.ai.base import AIProvider
from app.providers.ai.ollama import OllamaProvider


def create_ai_provider(settings: Settings | None = None) -> AIProvider:
    settings = settings or get_settings()
    if settings.ai_provider == "ollama":
        return OllamaProvider(
            settings.ollama_base_url, settings.ai_model, timeout=settings.ai_timeout_seconds
        )
    raise ValueError(f"Unknown AI provider: {settings.ai_provider}")
