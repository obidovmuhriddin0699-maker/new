from typing import Any

from app.agents.base import BaseAgent
from app.agents.schemas import StrategyOutput
from app.agents.structured import GenerationMeta
from app.models import BrandProfile


class ContentStrategist(BaseAgent):
    name = "content_strategist"

    async def recommend(
        self,
        brand: BrandProfile,
        *,
        language: str,
        goals: list[str] | None = None,
        performance: dict[str, Any] | None = None,
        user_request: str | None = None,
    ) -> tuple[StrategyOutput, GenerationMeta]:
        basis = (
            "Performance data is provided below; base recommendations on it."
            if performance
            else "No performance data is available yet. Say so where relevant and do not "
            "claim anything about what performs best."
        )
        return await self._run(
            task="strategy",
            brand=brand,
            language=language,
            instructions=(
                "Propose a content strategy: 2-6 content pillars with rationale, concrete "
                f"recommendations and risks. {basis}"
            ),
            schema=StrategyOutput,
            goals=goals or brand.content_goals,
            performance_data=performance,
            user_request=user_request,
        )
