"""Unit tests for GeminiProvider and GroqProvider."""

import pytest
import respx
import httpx

from app.providers.ai.gemini import GeminiProvider, GEMINI_API_BASE
from app.providers.ai.groq import GroqProvider, GROQ_API_BASE


@pytest.mark.asyncio
@respx.mock
async def test_gemini_provider_generate_text():
    respx.post(f"{GEMINI_API_BASE}/models/gemini-1.5-pro:generateContent").respond(
        status_code=200,
        json={
            "candidates": [
                {
                    "content": {
                        "parts": [{"text": "Salom! Men Gemini AI modeliman."}]
                    }
                }
            ]
        },
    )

    provider = GeminiProvider(api_key="test_gemini_key", model="gemini-1.5-pro")
    resp = await provider.generate_text("Salom")
    assert resp.text == "Salom! Men Gemini AI modeliman."
    assert resp.provider == "gemini"
    assert resp.model == "gemini-1.5-pro"
    await provider.aclose()


@pytest.mark.asyncio
@respx.mock
async def test_gemini_provider_health():
    respx.get(f"{GEMINI_API_BASE}/models/gemini-1.5-pro").respond(status_code=200, json={})
    provider = GeminiProvider(api_key="test_gemini_key", model="gemini-1.5-pro")
    status = await provider.health()
    assert status.available is True
    assert status.model_installed is True
    await provider.aclose()


@pytest.mark.asyncio
@respx.mock
async def test_groq_provider_generate_text():
    respx.post(f"{GROQ_API_BASE}/chat/completions").respond(
        status_code=200,
        json={
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": "Salom! Men Groq Llama 3 modeliman.",
                    }
                }
            ]
        },
    )

    provider = GroqProvider(api_key="test_groq_key", model="llama-3.3-70b-versatile")
    resp = await provider.generate_text("Salom")
    assert resp.text == "Salom! Men Groq Llama 3 modeliman."
    assert resp.provider == "groq"
    assert resp.model == "llama-3.3-70b-versatile"
    await provider.aclose()


@pytest.mark.asyncio
@respx.mock
async def test_groq_provider_health():
    respx.get(f"{GROQ_API_BASE}/models").respond(status_code=200, json={})
    provider = GroqProvider(api_key="test_groq_key", model="llama-3.3-70b-versatile")
    status = await provider.health()
    assert status.available is True
    assert status.model_installed is True
    await provider.aclose()
