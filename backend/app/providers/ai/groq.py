"""Groq AI provider (Llama 3.3 70B, Qwen, Mixtral).

Ultra-fast OpenAI-compatible LLM inference.
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

logger = logging.getLogger("app.providers.ai.groq")

GROQ_API_BASE = "https://api.groq.com/openai/v1"


class GroqProvider(AIProvider):
    name = "groq"

    def __init__(
        self,
        api_key: str,
        model: str = "llama-3.3-70b-versatile",
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
                "GROQ_API_KEY o'rnatilmagan. .env faylida GROQ_API_KEY ni sozlang."
            )

        url = f"{GROQ_API_BASE}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        messages: list[dict[str, str]] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        body: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
        }
        if max_tokens:
            body["max_tokens"] = max_tokens
        if json_mode:
            body["response_format"] = {"type": "json_object"}

        try:
            resp = await self._client.post(url, headers=headers, json=body)
        except httpx.TimeoutException as exc:
            msg = f"Groq API javob berishda vaqt tugadi ({self._timeout}s)"
            raise AIProviderTimeoutError(msg) from exc
        except httpx.HTTPError as exc:
            raise AIProviderUnavailableError(f"Groq API ga ulanishda xato: {exc}") from exc

        if resp.status_code == 404:
            raise AIModelNotFoundError(f"Groq modeli topilmadi: {self.model}")
        if resp.status_code != 200:
            error_msg = resp.text
            try:
                err_data = resp.json().get("error", {})
                error_msg = err_data.get("message", resp.text)
            except Exception:  # noqa: S110
                pass
            raise AIProviderError(f"Groq API xatoligi ({resp.status_code}): {error_msg}")

        data = resp.json()
        choices = data.get("choices", [])
        if not choices:
            raise AIInvalidResponseError("Groq bo'sh javob qaytardi")

        message = choices[0].get("message", {})
        text = message.get("content", "")
        if len(text) > self.max_response_chars:
            msg = f"Groq javobi ruxsat etilgan hajmdan oshdi: {len(text)} belgi"
            raise AIInvalidResponseError(msg)

        return AIResponse(
            text=text,
            model=self.model,
            provider=self.name,
            raw={"usage": data.get("usage", {})},
        )

    async def health(self) -> ProviderStatus:
        if not self.api_key:
            return ProviderStatus(
                provider=self.name,
                model=self.model,
                available=False,
                model_installed=False,
                error_code="missing_api_key",
                message="GROQ_API_KEY o'rnatilmagan",
            )

        url = f"{GROQ_API_BASE}/models"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        try:
            resp = await self._client.get(url, headers=headers)
            if resp.status_code == 200:
                return ProviderStatus(
                    provider=self.name,
                    model=self.model,
                    available=True,
                    model_installed=True,
                    message="Groq tayyor",
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
