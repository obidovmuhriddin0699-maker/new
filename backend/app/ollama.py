import os
from typing import Any

import httpx
from fastapi import HTTPException, status


class OllamaAdapter:
    def __init__(
        self,
        base_url: str | None = None,
        model: str | None = None,
        timeout_seconds: float = 120,
        max_output_tokens: int = 2048,
    ) -> None:
        self.base_url = (base_url or os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")).rstrip(
            "/"
        )
        self.model = model or os.getenv("OLLAMA_MODEL", "qwen2.5-coder:3b")
        self.timeout_seconds = timeout_seconds
        self.max_output_tokens = max_output_tokens

    def chat(
        self,
        prompt: str,
        system: str | None = None,
        temperature: float | None = None,
    ) -> dict[str, str]:
        messages: list[dict[str, str]] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        options: dict[str, int | float] = {"num_predict": self.max_output_tokens}
        if temperature is not None:
            options["temperature"] = temperature
        try:
            with httpx.Client(timeout=self.timeout_seconds) as client:
                response = client.post(
                    f"{self.base_url}/api/chat",
                    json={
                        "model": self.model,
                        "messages": messages,
                        "stream": False,
                        "options": options,
                    },
                )
                response.raise_for_status()
                payload: Any = response.json()
        except (httpx.RequestError, httpx.HTTPStatusError, ValueError) as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Local AI service is unavailable",
            ) from exc

        content = payload.get("message", {}).get("content") if isinstance(payload, dict) else None
        if not isinstance(content, str):
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Local AI service returned an invalid response",
            )
        return {"model": self.model, "response": content}


def get_ollama_adapter() -> OllamaAdapter:
    return OllamaAdapter()
