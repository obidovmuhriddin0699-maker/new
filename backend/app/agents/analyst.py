"""AI Analyst: turns computed weekly facts into a short report and recommendations.

The facts (numbers) are computed by code from stored Meta insights. The model only
phrases them. A per-report schema rejects any number that is not in the facts and any
content id that is not in the facts; the structured-output repair loop then asks the
model to fix it, and if it still fails the caller keeps the rule-based text.
"""

import re
from typing import Annotated, Any

from pydantic import Field, model_validator

from app.agents.base import BaseAgent
from app.agents.schemas import AIModel, Medium
from app.agents.structured import GenerationMeta
from app.models import BrandProfile

NUMBER = re.compile(r"\d+(?:[.,]\d+)?")


class Highlight(AIModel):
    content_id: int
    reason: Medium


class AnalystOutput(AIModel):
    summary: Annotated[str, Field(min_length=1, max_length=1500)]
    highlights: list[Highlight] = Field(default_factory=list, max_length=5)
    recommendations: list[Medium] = Field(min_length=1, max_length=6)


def _norm(token: str) -> str:
    value = token.replace(",", ".")
    if "." in value:
        value = value.rstrip("0").rstrip(".")
    return value


def allowed_numbers(facts: Any) -> set[str]:
    """Every number that appears anywhere in the facts, in the forms a writer might use."""
    out: set[str] = set()

    def walk(v: Any) -> None:
        if isinstance(v, bool) or v is None:
            return
        if isinstance(v, int | float):
            out.add(_norm(str(v)))
            if isinstance(v, float):
                for digits in (0, 1, 2):
                    out.add(_norm(f"{v:.{digits}f}"))
        elif isinstance(v, str):
            out.update(_norm(t) for t in NUMBER.findall(v))
        elif isinstance(v, dict):
            for item in v.values():
                walk(item)
        elif isinstance(v, list | tuple):
            for item in v:
                walk(item)

    walk(facts)
    return out


def unknown_numbers(text: str, allowed: set[str], extra: set[str] = frozenset()) -> list[str]:
    return [t for t in NUMBER.findall(text) if _norm(t) not in allowed and _norm(t) not in extra]


# Small counts are fine in advice ("2 ta Reels"), but never in the factual summary.
ADVICE_NUMBERS = {str(n) for n in range(1, 11)}


def checked_schema(facts: dict[str, Any]) -> type[AnalystOutput]:
    allowed = allowed_numbers(facts)
    content_ids = {int(i["content_id"]) for i in facts.get("content", [])}

    class CheckedAnalystOutput(AnalystOutput):
        @model_validator(mode="after")
        def _only_facts(self) -> "CheckedAnalystOutput":
            factual = " ".join([self.summary, *(h.reason for h in self.highlights)])
            bad = unknown_numbers(factual, allowed)
            bad += [
                n for r in self.recommendations for n in unknown_numbers(r, allowed, ADVICE_NUMBERS)
            ]
            if bad:
                raise ValueError(
                    f"These numbers are not in FACTS: {sorted(set(bad))}. Use only numbers "
                    "copied from FACTS, or write without numbers."
                )
            unknown_ids = [h.content_id for h in self.highlights if h.content_id not in content_ids]
            if unknown_ids:
                raise ValueError(f"content_id {unknown_ids} is not in FACTS.content")
            return self

    return CheckedAnalystOutput


class AnalyticsAnalyst(BaseAgent):
    name = "analytics_analyst"

    async def weekly_report(
        self, brand: BrandProfile, *, language: str, facts: dict[str, Any]
    ) -> tuple[AnalystOutput, GenerationMeta]:
        return await self._run(
            task="weekly_analytics_report",
            brand=brand,
            language=language,
            instructions=(
                "Write a short weekly Instagram performance report for the brand owner from "
                "FACTS only. Say which content performed best this week and why that is "
                "plausible from its format/topic, without claiming certainty about causes. "
                "Every number you write must be copied exactly from FACTS. Metrics that are "
                "missing from FACTS are unknown: say they are unavailable, never estimate. "
                "If FACTS has little data, say so. Then give 2-5 practical recommendations "
                "for next week's content strategy."
            ),
            schema=checked_schema(facts),
            facts=facts,
        )
