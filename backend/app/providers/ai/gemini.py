"""Google Gemini AI provider (Gemini 1.5 Pro, 1.5 Flash, 2.0 Flash).

Connects directly via Google Generative Language REST API.
Supports system instructions, temperature, and structured JSON mode.
"""

import logging
from typing import Any

import httpx

from app.providers.ai.base import (
    AIInvalidResponseError,
    AIModelNotFoundError,
    AIProvider,
    AIProviderError,
    AIProviderTimeoutError,
    AIProviderUnavailableError,
    AIResponse,
    ProviderStatus,
)

logger = logging.getLogger("app.providers.ai.gemini")

GEMINI_API_BASE = "https://generativelanguage.googleapis.com/v1beta"


class GeminiProvider(AIProvider):
    name = "gemini"

    def __init__(
        self,
        api_key: str,
        model: str = "gemini-1.5-pro",
        *,
        timeout: float = 60.0,
        max_response_chars: int = 60_000,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self.api_key = api_key
        self.model = model
        self.max_response_chars = max_response_chars
        self._timeout = timeout
        self._client = client or httpx.AsyncClient(timeout=timeout)

    async def aclose(self) -> None:
        await self._client.aclose()

    async def generate_text(
        self,
        prompt: str,
        *,
        system: str | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        json_mode: bool = False,
    ) -> AIResponse:
        if not self.api_key:
            raise AIProviderUnavailableError(
                "GEMINI_API_KEY o'rnatilmagan. .env faylida GEMINI_API_KEY ni sozlang."
            )

        url = f"{GEMINI_API_BASE}/models/{self.model}:generateContent"
        params = {"key": self.api_key}

        generation_config: dict[str, Any] = {
            "temperature": temperature,
        }
        if max_tokens:
            generation_config["maxOutputTokens"] = max_tokens
        if json_mode:
            generation_config["responseMimeType"] = "application/json"

        body: dict[str, Any] = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": prompt}],
                }
            ],
            "generationConfig": generation_config,
        }

        if system:
            body["system_instruction"] = {
                "parts": [{"text": system}],
            }

        try:
            resp = await self._client.post(url, params=params, json=body)
        except httpx.TimeoutException as exc:
            msg = f"Gemini API javob berishda vaqt tugadi ({self._timeout}s)"
            raise AIProviderTimeoutError(msg) from exc
        except httpx.HTTPError as exc:
            raise AIProviderUnavailableError(f"Gemini API ga ulanishda xato: {exc}") from exc

        if resp.status_code == 404:
            raise AIModelNotFoundError(f"Gemini modeli topilmadi: {self.model}")
        if resp.status_code != 200:
            error_msg = resp.text
            try:
                err_data = resp.json().get("error", {})
                error_msg = err_data.get("message", resp.text)
            except Exception:  # noqa: S110
                pass
            raise AIProviderError(f"Gemini API xatoligi ({resp.status_code}): {error_msg}")

        data = resp.json()
        candidates = data.get("candidates", [])
        if not candidates:
            raise AIInvalidResponseError("Gemini bo'sh javob qaytardi")

        parts = candidates[0].get("content", {}).get("parts", [])
        if not parts:
            raise AIInvalidResponseError("Gemini javobida matn qismi yo'q")

        text = parts[0].get("text", "")
        if len(text) > self.max_response_chars:
            msg = f"Gemini javobi ruxsat etilgan hajmdan oshdi: {len(text)} belgi"
            raise AIInvalidResponseError(msg)

        return AIResponse(
            text=text,
            model=self.model,
            provider=self.name,
            raw={"candidates_count": len(candidates)},
        )

    async def health(self) -> ProviderStatus:
        if not self.api_key:
            return ProviderStatus(
                provider=self.name,
                model=self.model,
                available=False,
                model_installed=False,
                error_code="missing_api_key",
                message="GEMINI_API_KEY o'rnatilmagan",
            )

        url = f"{GEMINI_API_BASE}/models/{self.model}"
        params = {"key": self.api_key}
        try:
            resp = await self._client.get(url, params=params)
            if resp.status_code == 200:
                return ProviderStatus(
                    provider=self.name,
                    model=self.model,
                    available=True,
                    model_installed=True,
                    message="Gemini tayyor",
                )
            return ProviderStatus(
                provider=self.name,
                model=self.model,
                available=False,
                model_installed=False,
                error_code=f"http_{resp.status_code}",
                message=resp.text,
            )
        except Exception as exc:
            return ProviderStatus(
                provider=self.name,
                model=self.model,
                available=False,
                model_installed=False,
                error_code="connection_error",
                message=str(exc),
            )
