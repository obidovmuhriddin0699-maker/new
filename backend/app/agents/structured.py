"""Structured generation: prompt -> provider -> JSON extraction -> schema validation.

* The provider's text is untrusted and parsed defensively.
* On invalid output the model gets one repair attempt (configurable), with the
  validation errors; if it still fails, ``AIOutputValidationError`` is raised.
  Nothing is ever substituted for a failed generation.
* Prompts are not logged or stored; only a SHA-256 fingerprint is recorded.
"""

import asyncio
import hashlib
import json
import re
import time
from dataclasses import dataclass, field
from typing import Any, TypeVar

from pydantic import BaseModel, ValidationError

from app.core.config import get_settings
from app.providers.ai.base import AIOutputValidationError, AIProvider

T = TypeVar("T", bound=BaseModel)

PROMPT_VERSION = "2026-10-p3.1"
_FENCE = re.compile(r"^```(?:json)?\s*|\s*```$", re.IGNORECASE)


@dataclass(slots=True)
class GenerationMeta:
    provider: str
    model: str
    task: str
    attempts: int
    duration_ms: int
    prompt_version: str = PROMPT_VERSION
    prompt_sha256: str = ""
    validation_errors: list[str] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return {
            "provider": self.provider,
            "model": self.model,
            "task": self.task,
            "attempts": self.attempts,
            "duration_ms": self.duration_ms,
            "prompt_version": self.prompt_version,
            "prompt_sha256": self.prompt_sha256,
        }


def extract_json(text: str) -> Any:
    """Parse a JSON object from model text (tolerates code fences / leading prose)."""
    cleaned = _FENCE.sub("", text.strip())
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass
    start, end = cleaned.find("{"), cleaned.rfind("}")
    if start == -1 or end <= start:
        raise ValueError("no JSON object found in model output")
    return json.loads(cleaned[start : end + 1])


def _errors(exc: ValidationError) -> list[str]:
    out = []
    for err in exc.errors()[:10]:
        loc = ".".join(str(p) for p in err.get("loc", ()))
        out.append(f"{loc or 'root'}: {err.get('msg')}")
    return out


async def generate_structured(
    provider: AIProvider,
    *,
    task: str,
    system: str,
    prompt: str,
    schema: type[T],
    max_attempts: int | None = None,
) -> tuple[T, GenerationMeta]:
    settings = get_settings()
    attempts_allowed = max(1, max_attempts or settings.ai_structured_max_attempts)
    started = time.perf_counter()
    current_prompt = prompt
    last_errors: list[str] = []
    for attempt in range(1, attempts_allowed + 1):
        response = await provider.generate_text(
            current_prompt,
            system=system,
            temperature=settings.ai_temperature,
            max_tokens=settings.ai_max_output_tokens,
            json_mode=True,
        )
        try:
            data = extract_json(response.text)
            if not isinstance(data, dict):
                raise ValueError("model output must be a JSON object")
            result = schema.model_validate(data)
        except (ValueError, ValidationError) as exc:
            last_errors = _errors(exc) if isinstance(exc, ValidationError) else [str(exc)]
            current_prompt = (
                f"{prompt}\n\nYOUR PREVIOUS ANSWER WAS INVALID:\n- "
                + "\n- ".join(last_errors)
                + "\nReturn ONLY one corrected JSON object that matches the schema."
            )
            continue
        meta = GenerationMeta(
            provider=response.provider,
            model=response.model,
            task=task,
            attempts=attempt,
            duration_ms=int((time.perf_counter() - started) * 1000),
            prompt_sha256=hashlib.sha256(prompt.encode()).hexdigest(),
        )
        return result, meta
    raise AIOutputValidationError(
        f"The AI model did not return valid '{task}' output after {attempts_allowed} attempt(s).",
        errors=last_errors,
    )


def run_sync(coro: Any) -> Any:
    """Run a coroutine from synchronous code (FastAPI threadpool or Celery worker)."""
    return asyncio.run(coro)
