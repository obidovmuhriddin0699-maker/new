import httpx
import pytest
import respx

from app.core.config import Settings
from app.providers.ai.base import (
    AIInvalidResponseError,
    AIModelNotFoundError,
    AIProviderTimeoutError,
    AIProviderUnavailableError,
)
from app.providers.ai.factory import create_ai_provider
from app.providers.ai.mock import MockAIProvider
from app.providers.ai.ollama import OllamaProvider

BASE = "http://ollama.test:11434"


@respx.mock
async def test_json_mode_sets_ollama_format():
    route = respx.post(f"{BASE}/api/generate").mock(
        return_value=httpx.Response(200, json={"response": "{}"})
    )
    await OllamaProvider(BASE, "qwen2.5:3b").generate_text("x", json_mode=True)
    assert b'"format":"json"' in route.calls.last.request.read()


@respx.mock
@pytest.mark.parametrize(
    "response",
    [
        httpx.Response(200, text="<html>not json</html>"),
        httpx.Response(200, json=["not", "an", "object"]),
        httpx.Response(200, json={"done": True}),
        httpx.Response(200, json={"response": "   "}),
        httpx.Response(200, json={"response": 42}),
    ],
)
async def test_malformed_ollama_responses(response):
    respx.post(f"{BASE}/api/generate").mock(return_value=response)
    with pytest.raises(AIInvalidResponseError):
        await OllamaProvider(BASE, "qwen2.5:3b").generate_text("x")


@respx.mock
async def test_oversized_response_rejected():
    respx.post(f"{BASE}/api/generate").mock(
        return_value=httpx.Response(200, json={"response": "x" * 500})
    )
    with pytest.raises(AIInvalidResponseError):
        await OllamaProvider(BASE, "m", max_response_chars=100).generate_text("x")


@respx.mock
@pytest.mark.parametrize(
    ("side_effect", "error"),
    [
        (httpx.ConnectError("refused"), AIProviderUnavailableError),
        (httpx.ConnectTimeout("t"), AIProviderUnavailableError),
        (httpx.ReadTimeout("slow"), AIProviderTimeoutError),
    ],
)
async def test_unavailable_and_timeout(side_effect, error):
    respx.post(f"{BASE}/api/generate").mock(side_effect=side_effect)
    with pytest.raises(error) as exc:
        await OllamaProvider(BASE, "m").generate_text("x")
    assert exc.value.category in {"provider_unavailable", "timeout"}


@respx.mock
async def test_missing_model_category():
    respx.post(f"{BASE}/api/generate").mock(return_value=httpx.Response(404))
    with pytest.raises(AIModelNotFoundError) as exc:
        await OllamaProvider(BASE, "m").generate_text("x")
    assert exc.value.category == "model_not_found"


@respx.mock
async def test_health_with_malformed_tags():
    respx.get(f"{BASE}/api/tags").mock(return_value=httpx.Response(200, text="oops"))
    status = await OllamaProvider(BASE, "m").health()
    assert not status.available and status.error_code == "ai_invalid_response"


async def test_mock_provider_queue_responder_and_errors():
    p = MockAIProvider(["first", AIProviderTimeoutError("t")], responder=lambda pr, s: "dyn")
    assert (await p.generate_text("a")).text == "first"
    with pytest.raises(AIProviderTimeoutError):
        await p.generate_text("b")
    assert (await p.generate_text("c")).text == "dyn"
    assert p.calls[0]["prompt"] == "a" and len(p.calls) == 3
    assert (await p.health()).available
    r = await MockAIProvider().generate_text("TASK: hashtags")
    assert r.provider == "mock" and "#" in r.text


def test_factory_mock_and_production_guard(monkeypatch):
    monkeypatch.setenv("AI_PROVIDER", "mock")
    assert isinstance(create_ai_provider(Settings(_env_file=None)), MockAIProvider)
    s = Settings(_env_file=None).model_copy(update={"app_env": "production"})
    with pytest.raises(ValueError):
        create_ai_provider(s)


def test_production_config_rejects_mock(monkeypatch):
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("JWT_SECRET_KEY", "x" * 48)
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://u:p@db/x")
    monkeypatch.setenv("CORS_ORIGINS", "https://panel.example.com")
    monkeypatch.setenv("AI_PROVIDER", "mock")
    from pydantic import ValidationError

    with pytest.raises(ValidationError, match="AI_PROVIDER=mock"):
        Settings(_env_file=None)


def test_default_model_is_configurable(monkeypatch):
    assert Settings(_env_file=None).ai_model == "qwen2.5:3b"
    monkeypatch.setenv("AI_MODEL", "llama3.2:3b")
    assert create_ai_provider(Settings(_env_file=None)).model == "llama3.2:3b"
