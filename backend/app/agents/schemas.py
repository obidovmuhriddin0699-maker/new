"""Validated schemas for AI-generated output.

Model output is untrusted: it is parsed and validated against these schemas
before anything is saved. Limits keep a misbehaving model from producing
oversized or malformed records. Instagram limits used here (2200-char caption,
30 hashtags, 10 carousel items) must be re-verified against Meta docs in PHASE 8.
"""

from datetime import date
from enum import StrEnum
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.models.enums import ContentType

MAX_CAPTION = 2200
MAX_HASHTAGS = 30
MIN_CAROUSEL_SLIDES = 2
MAX_CAROUSEL_SLIDES = 10
MAX_REELS_SECONDS = 180

Short = Annotated[str, Field(min_length=1, max_length=200)]
Medium = Annotated[str, Field(min_length=1, max_length=600)]


def _clean_text(value: object) -> object:
    if isinstance(value, str):
        # Drop control characters (except newline/tab) a model may emit.
        value = "".join(ch for ch in value if ch in "\n\t" or ord(ch) >= 32).strip()
    return value


def normalize_hashtags(values: list[str]) -> list[str]:
    out: list[str] = []
    for raw in values:
        tag = str(raw).strip().replace(" ", "")
        if not tag:
            continue
        if not tag.startswith("#"):
            tag = "#" + tag
        if len(tag) > 60:
            continue
        if tag.lower() not in {t.lower() for t in out}:
            out.append(tag)
    return out


class AIModel(BaseModel):
    model_config = ConfigDict(extra="ignore", str_strip_whitespace=True)

    @model_validator(mode="before")
    @classmethod
    def _strip_controls(cls, data: object) -> object:
        if isinstance(data, dict):
            return {k: _clean_text(v) for k, v in data.items()}
        return data


class Objective(StrEnum):
    EDUCATE = "EDUCATE"
    ENGAGE = "ENGAGE"
    SHOWCASE = "SHOWCASE"
    CONVERT = "CONVERT"
    AWARENESS = "AWARENESS"


class HashtagMixin(AIModel):
    hashtags: list[str] = Field(default_factory=list)

    @field_validator("hashtags", mode="before")
    @classmethod
    def _tags(cls, value: object) -> list[str]:
        if value is None:
            return []
        if isinstance(value, str):
            value = value.replace(",", " ").split()
        if not isinstance(value, list):
            raise ValueError("hashtags must be a list")
        tags = normalize_hashtags([str(v) for v in value])
        if len(tags) > MAX_HASHTAGS:
            raise ValueError(f"at most {MAX_HASHTAGS} hashtags")
        return tags


# ------------------------------------------------------------------ strategy / planning
class StrategyPillar(AIModel):
    name: Short
    rationale: Medium
    share_percent: int | None = Field(default=None, ge=0, le=100)


class StrategyOutput(AIModel):
    summary: Annotated[str, Field(min_length=1, max_length=1500)]
    pillars: list[StrategyPillar] = Field(min_length=1, max_length=8)
    recommendations: list[Medium] = Field(min_length=1, max_length=10)
    risks: list[Medium] = Field(default_factory=list, max_length=10)


class ContentIdea(AIModel):
    title: Short
    format: ContentType
    objective: Objective
    topic: Short
    hook: Medium
    summary: Annotated[str, Field(min_length=1, max_length=1000)]


class IdeasOutput(AIModel):
    ideas: list[ContentIdea] = Field(min_length=1, max_length=20)


class PlanItemDraft(AIModel):
    """What the model returns: a relative day, never a calendar date or a time of day."""

    day_offset: int = Field(ge=0, le=30)
    format: ContentType
    objective: Objective
    topic: Short
    title: Short


class PlanDraftOutput(AIModel):
    items: list[PlanItemDraft] = Field(min_length=1, max_length=31)
    notes: Annotated[str, Field(max_length=1000)] | None = None


class PlanItem(BaseModel):
    """Server-computed plan item (date derived from start date + offset)."""

    suggested_date: date
    weekday: str
    day_offset: int
    format: ContentType
    objective: Objective
    topic: str
    title: str
    status: Literal["PLANNED", "DRAFT_CREATED"] = "PLANNED"
    content_id: int | None = None


class ContentPlan(BaseModel):
    period: Literal["week", "month"]
    start_date: date
    end_date: date
    items: list[PlanItem]
    notes: str | None = None
    timing_basis: str = Field(
        description="Why these days were suggested. Not an optimal-time claim."
    )


# ------------------------------------------------------------------ content formats
class PostOutput(HashtagMixin):
    hook: Medium
    caption: Annotated[str, Field(min_length=1, max_length=MAX_CAPTION)]
    cta: Annotated[str, Field(min_length=1, max_length=300)]
    alt_text: Annotated[str, Field(max_length=500)] | None = None
    visual_prompt: Annotated[str, Field(max_length=1500)] | None = None


class CarouselSlide(AIModel):
    heading: Annotated[str, Field(min_length=1, max_length=80)]
    body: Annotated[str, Field(min_length=1, max_length=400)]


class CarouselOutput(HashtagMixin):
    title: Short
    slides: list[CarouselSlide] = Field(
        min_length=MIN_CAROUSEL_SLIDES, max_length=MAX_CAROUSEL_SLIDES
    )
    caption: Annotated[str, Field(min_length=1, max_length=MAX_CAPTION)]
    cta: Annotated[str, Field(min_length=1, max_length=300)]


class ReelsScene(AIModel):
    duration_seconds: float = Field(gt=0, le=60)
    visual: Medium
    on_screen_text: Annotated[str, Field(max_length=150)] | None = None
    narration: Annotated[str, Field(max_length=600)] | None = None


class ReelsScriptOutput(HashtagMixin):
    hook: Medium
    scenes: list[ReelsScene] = Field(min_length=1, max_length=20)
    cta: Annotated[str, Field(min_length=1, max_length=300)]
    caption: Annotated[str, Field(min_length=1, max_length=MAX_CAPTION)]
    approx_duration_seconds: float | None = Field(default=None, gt=0, le=MAX_REELS_SECONDS)

    @model_validator(mode="after")
    def _duration(self) -> "ReelsScriptOutput":
        total = sum(s.duration_seconds for s in self.scenes)
        if total > MAX_REELS_SECONDS:
            raise ValueError(f"scenes add up to {total:.0f}s (max {MAX_REELS_SECONDS}s)")
        # The server value is authoritative; the model's own estimate is replaced.
        self.approx_duration_seconds = round(total, 1)
        return self


class StoryFrame(AIModel):
    visual: Medium
    text: Annotated[str, Field(max_length=200)] | None = None
    interactive_element: Literal["poll", "question", "quiz", "slider", "none"] | None = None


class StoryOutput(AIModel):
    title: Short
    frames: list[StoryFrame] = Field(min_length=1, max_length=10)
    cta: Annotated[str, Field(max_length=300)] | None = None


class HashtagOutput(HashtagMixin):
    @model_validator(mode="after")
    def _non_empty(self) -> "HashtagOutput":
        if not self.hashtags:
            raise ValueError("at least one hashtag is required")
        return self


# ------------------------------------------------------------------ quality
class Severity(StrEnum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


class QualityFinding(BaseModel):
    severity: Severity
    code: str
    field: str
    message: str
    suggestion: str | None = None


class QualityReport(BaseModel):
    passed: bool = Field(description="False if any ERROR finding exists")
    score: int = Field(ge=0, le=100, description="Heuristic score; not a guarantee")
    findings: list[QualityFinding]
    checks: list[str]
    disclaimer: str = (
        "Automated, rule-based checks. They do not verify factual accuracy or predict "
        "business results; a human must review the content."
    )
