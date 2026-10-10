"""Shared base for pipeline agents.

Agents are plain service components: they receive a provider and a brand
profile, build prompts, call ``generate_structured`` and return validated
schema objects. They have no database access, no tools, and no way to
approve, schedule or publish. Persisting results is the job of
``AIContentService`` using an ``AgentActor`` with limited permissions.
"""

from typing import TypeVar

from pydantic import BaseModel

from app.agents.prompts import brand_system_prompt, task_prompt
from app.agents.structured import GenerationMeta, generate_structured
from app.models import BrandProfile
from app.providers.ai.base import AIProvider

T = TypeVar("T", bound=BaseModel)


class BaseAgent:
    name: str = "agent"

    def __init__(self, provider: AIProvider) -> None:
        self.provider = provider

    async def _run(
        self,
        *,
        task: str,
        brand: BrandProfile,
        language: str,
        instructions: str,
        schema: type[T],
        **context: object,
    ) -> tuple[T, GenerationMeta]:
        return await generate_structured(
            self.provider,
            task=task,
            system=brand_system_prompt(brand, language),
            prompt=task_prompt(task, instructions, schema.model_json_schema(), **context),
            schema=schema,
        )
