"""Ollama provider (local LLM). Failures become typed errors, never crashes.

Prompts are never logged here: they can contain brand data or user input.
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

logger = logging.getLogger(__name__)


class OllamaProvider(AIProvider):
    name = "ollama"

    def __init__(
        self,
        base_url: str,
        model: str,
        *,
        timeout: float = 120.0,
        max_response_chars: int = 60_000,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.max_response_chars = max_response_chars
        self._client = client or httpx.AsyncClient(base_url=self.base_url, timeout=timeout)

    async def generate_text(
        self,
        prompt: str,
        *,
        system: str | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        json_mode: bool = False,
    ) -> AIResponse:
        options: dict[str, Any] = {"temperature": temperature}
        if max_tokens:
            options["num_predict"] = max_tokens
        payload: dict[str, Any] = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": options,
        }
        if system:
            payload["system"] = system
        if json_mode:
            payload["format"] = "json"

        data = await self._post("/api/generate", payload)
        text = data.get("response")
        if not isinstance(text, str) or not text.strip():
            raise AIInvalidResponseError("Ollama returned an empty or malformed response.")
        if len(text) > self.max_response_chars:
            raise AIInvalidResponseError("Ollama response exceeded the allowed size.")
        return AIResponse(
            text=text.strip(),
            model=self.model,
            provider=self.name,
            raw={k: v for k, v in data.items() if k != "context"},
        )

    async def health(self) -> ProviderStatus:
        try:
            resp = await self._client.get("/api/tags", timeout=3.0)
            resp.raise_for_status()
        except (httpx.ConnectError, httpx.ConnectTimeout, httpx.ReadTimeout):
            return ProviderStatus(
                self.name,
                self.model,
                False,
                False,
                AIProviderUnavailableError.code,
                "Ollama is not reachable. Run 'ollama serve' and check OLLAMA_BASE_URL.",
            )
        except httpx.HTTPError as exc:
            return ProviderStatus(
                self.name, self.model, False, False, AIProviderError.code, type(exc).__name__
            )
        try:
            names = {m.get("name") for m in resp.json().get("models", [])}
        except (ValueError, AttributeError, TypeError):
            return ProviderStatus(
                self.name,
                self.model,
                False,
                False,
                AIInvalidResponseError.code,
                "Ollama returned an unexpected /api/tags response.",
            )
        installed = self.model in names or f"{self.model}:latest" in names
        return ProviderStatus(
            self.name,
            self.model,
            True,
            installed,
            None if installed else AIModelNotFoundError.code,
            None if installed else f"Model not installed. Run 'ollama pull {self.model}'.",
        )

    async def aclose(self) -> None:
        await self._client.aclose()

    async def _post(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        try:
            resp = await self._client.post(path, json=payload)
        except (httpx.ConnectError, httpx.ConnectTimeout) as exc:
            # The URL is logged server-side only; client messages stay generic.
            logger.warning("ollama_unreachable", extra={"ollama_base_url": self.base_url})
            raise AIProviderUnavailableError(
                "Ollama is not reachable. Run 'ollama serve' and check OLLAMA_BASE_URL."
            ) from exc
        except httpx.TimeoutException as exc:
            raise AIProviderTimeoutError("Ollama did not respond in time.") from exc
        except httpx.HTTPError as exc:
            raise AIProviderError(f"Ollama request failed: {type(exc).__name__}") from exc

        if resp.status_code == 404:
            raise AIModelNotFoundError(
                f"Model '{self.model}' is not installed. Run 'ollama pull {self.model}'."
            )
        if resp.status_code >= 400:
            raise AIProviderError(f"Ollama returned HTTP {resp.status_code}.")
        try:
            data = resp.json()
        except ValueError as exc:
            raise AIInvalidResponseError("Ollama returned a non-JSON response.") from exc
        if not isinstance(data, dict):
            raise AIInvalidResponseError("Ollama returned an unexpected response shape.")
        return data
