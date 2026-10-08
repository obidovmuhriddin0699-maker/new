from datetime import date, timedelta

from app.agents.base import BaseAgent
from app.agents.schemas import (
    ContentPlan,
    IdeasOutput,
    PlanDraftOutput,
    PlanItem,
)
from app.agents.structured import GenerationMeta
from app.models import BrandProfile
from app.models.enums import ContentType
from app.providers.ai.base import AIOutputValidationError

PERIOD_DAYS = {"week": 7, "month": 30}
WEEKDAYS = ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY"]


class ContentPlanner(BaseAgent):
    name = "content_planner"

    async def ideas(
        self,
        brand: BrandProfile,
        *,
        language: str,
        count: int,
        formats: list[ContentType] | None = None,
        topic: str | None = None,
        user_request: str | None = None,
    ) -> tuple[IdeasOutput, GenerationMeta]:
        result, meta = await self._run(
            task="ideas",
            brand=brand,
            language=language,
            instructions=f"Generate {count} distinct Instagram content ideas.",
            schema=IdeasOutput,
            allowed_formats=[f.value for f in formats] if formats else None,
            focus_topic=topic,
            user_request=user_request,
        )
        ideas = result.ideas
        if formats:
            ideas = [i for i in ideas if i.format in formats]
        result.ideas = ideas[:count]
        if not result.ideas:
            raise AIOutputValidationError("The model returned no ideas in the requested formats.")
        return result, meta

    async def plan(
        self,
        brand: BrandProfile,
        *,
        language: str,
        start_date: date,
        period: str,
        posts_per_week: int,
        user_request: str | None = None,
        has_analytics: bool = False,
    ) -> tuple[ContentPlan, GenerationMeta]:
        days = PERIOD_DAYS[period]
        draft, meta = await self._run(
            task="content_plan",
            brand=brand,
            language=language,
            instructions=(
                f"Create a {period} content plan with about {posts_per_week} items per week. "
                f"Use day_offset 0..{days - 1} relative to the start date. Mix formats and "
                "objectives. Do not give times of day."
            ),
            schema=PlanDraftOutput,
            start_weekday=WEEKDAYS[start_date.weekday()],
            user_request=user_request,
        )
        items = sorted((i for i in draft.items if i.day_offset < days), key=lambda i: i.day_offset)
        if not items:
            raise AIOutputValidationError("The model returned no plan items inside the period.")
        plan_items = []
        for item in items:
            day = start_date + timedelta(days=item.day_offset)
            plan_items.append(
                PlanItem(
                    suggested_date=day,
                    weekday=WEEKDAYS[day.weekday()],
                    day_offset=item.day_offset,
                    format=item.format,
                    objective=item.objective,
                    topic=item.topic,
                    title=item.title,
                )
            )
        basis = (
            "Suggested days are based on available account analytics."
            if has_analytics
            else "Suggested days only spread content across the period. They are not based "
            "on account analytics and are not claimed to be optimal posting times."
        )
        return (
            ContentPlan(
                period=period,  # type: ignore[arg-type]
                start_date=start_date,
                end_date=start_date + timedelta(days=days - 1),
                items=plan_items,
                notes=draft.notes,
                timing_basis=basis,
            ),
            meta,
        )
