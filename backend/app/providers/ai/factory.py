from app.core.config import Settings, get_settings
from app.providers.ai.base import AIProvider
from app.providers.ai.gemini import GeminiProvider
from app.providers.ai.groq import GroqProvider
from app.providers.ai.mock import MockAIProvider
from app.providers.ai.ollama import OllamaProvider


def create_ai_provider(settings: Settings | None = None) -> AIProvider:
    settings = settings or get_settings()

    if settings.ai_provider == "gemini":
        api_key = settings.gemini_api_key.get_secret_value()
        return GeminiProvider(
            api_key=api_key,
            model=settings.gemini_model,
            timeout=settings.ai_timeout_seconds,
            max_response_chars=settings.ai_max_response_chars,
        )

    if settings.ai_provider == "groq":
        api_key = settings.groq_api_key.get_secret_value()
        return GroqProvider(
            api_key=api_key,
            model=settings.groq_model,
            timeout=settings.ai_timeout_seconds,
            max_response_chars=settings.ai_max_response_chars,
        )

    if settings.ai_provider == "ollama":
        return OllamaProvider(
            settings.ollama_base_url,
            settings.ai_model,
            timeout=settings.ai_timeout_seconds,
            max_response_chars=settings.ai_max_response_chars,
        )

    if settings.ai_provider == "mock":
        if settings.app_env == "production":
            raise ValueError("The mock AI provider cannot be used in production")
        return MockAIProvider()

    raise ValueError(f"Unknown AI provider: {settings.ai_provider}")
