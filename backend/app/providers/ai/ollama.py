"""Ollama provider (local LLM). Failures become typed errors, never crashes."""

from typing import Any

import httpx

from app.providers.ai.base import (
    AIModelNotFoundError,
    AIProvider,
    AIProviderError,
    AIProviderTimeoutError,
    AIProviderUnavailableError,
    AIResponse,
    ProviderStatus,
)


class OllamaProvider(AIProvider):
    name = "ollama"

    def __init__(
        self,
        base_url: str,
        model: str,
        *,
        timeout: float = 120.0,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self._client = client or httpx.AsyncClient(base_url=self.base_url, timeout=timeout)

    async def generate_text(
        self,
        prompt: str,
        *,
        system: str | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
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

        data = await self._post("/api/generate", payload)
        return AIResponse(
            text=str(data.get("response", "")).strip(),
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
                f"Ollama is not reachable at {self.base_url}. Run 'ollama serve'.",
            )
        except httpx.HTTPError as exc:
            return ProviderStatus(
                self.name, self.model, False, False, AIProviderError.code, type(exc).__name__
            )
        names = {m.get("name") for m in resp.json().get("models", [])}
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
            raise AIProviderUnavailableError(
                f"Ollama is not reachable at {self.base_url}. Run 'ollama serve'."
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
        return resp.json()
