import httpx
import pytest
import respx

from app.providers.ai.base import (
    AIModelNotFoundError,
    AIProvider,
    AIProviderTimeoutError,
    AIProviderUnavailableError,
)
from app.providers.ai.factory import create_ai_provider
from app.providers.ai.ollama import OllamaProvider

BASE = "http://ollama.test:11434"


def test_factory_creates_ollama_with_default_model():
    provider = create_ai_provider()
    assert isinstance(provider, AIProvider)
    assert isinstance(provider, OllamaProvider)
    assert provider.model == "qwen2.5:3b"
    assert provider.base_url == BASE


@respx.mock
async def test_generate_text_success():
    route = respx.post(f"{BASE}/api/generate").mock(
        return_value=httpx.Response(200, json={"response": " Salom! ", "done": True})
    )
    provider = OllamaProvider(BASE, "qwen2.5:3b")
    result = await provider.generate_text("Salom", system="You are helpful")
    await provider.aclose()
    assert result.text == "Salom!"
    assert result.provider == "ollama"
    sent = route.calls.last.request.read()
    assert b'"model":"qwen2.5:3b"' in sent and b'"stream":false' in sent


@respx.mock
async def test_ollama_down_raises_typed_error():
    respx.post(f"{BASE}/api/generate").mock(side_effect=httpx.ConnectError("refused"))
    provider = OllamaProvider(BASE, "qwen2.5:3b")
    with pytest.raises(AIProviderUnavailableError) as exc:
        await provider.generate_text("x")
    assert "ollama serve" in exc.value.message


@respx.mock
async def test_model_missing_raises_typed_error():
    respx.post(f"{BASE}/api/generate").mock(return_value=httpx.Response(404, json={}))
    provider = OllamaProvider(BASE, "qwen2.5:3b")
    with pytest.raises(AIModelNotFoundError) as exc:
        await provider.generate_text("x")
    assert "ollama pull qwen2.5:3b" in exc.value.message


@respx.mock
async def test_timeout_raises_typed_error():
    respx.post(f"{BASE}/api/generate").mock(side_effect=httpx.ReadTimeout("slow"))
    provider = OllamaProvider(BASE, "qwen2.5:3b")
    with pytest.raises(AIProviderTimeoutError):
        await provider.generate_text("x")


@respx.mock
async def test_health_reports_model_installed():
    respx.get(f"{BASE}/api/tags").mock(
        return_value=httpx.Response(200, json={"models": [{"name": "qwen2.5:3b"}]})
    )
    status = await OllamaProvider(BASE, "qwen2.5:3b").health()
    assert status.available and status.model_installed


@respx.mock
async def test_health_reports_model_missing():
    respx.get(f"{BASE}/api/tags").mock(return_value=httpx.Response(200, json={"models": []}))
    status = await OllamaProvider(BASE, "qwen2.5:3b").health()
    assert status.available and not status.model_installed
    assert status.error_code == "ai_model_not_found"


@respx.mock
def test_ai_status_endpoint_when_ollama_down(client, auth_headers):
    respx.get(f"{BASE}/api/tags").mock(side_effect=httpx.ConnectError("refused"))
    resp = client.get("/api/v1/system/ai-status", headers=auth_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["available"] is False
    assert body["error_code"] == "ai_provider_unavailable"
    # backend is still alive
    assert client.get("/health").status_code == 200


def test_ai_status_requires_auth(client):
    assert client.get("/api/v1/system/ai-status").status_code == 401
