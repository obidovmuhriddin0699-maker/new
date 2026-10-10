"""AI pipeline API schemas: request limits and response shapes."""

from datetime import date, datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.agents.schemas import MAX_CAROUSEL_SLIDES, MIN_CAROUSEL_SLIDES, QualityReport
from app.models.enums import AIJobStatus, ContentType

Language = Literal["uz", "ru", "en"]
MAX_INSTRUCTIONS = 1000


class AIStatusResponse(BaseModel):
    provider: str
    model: str
    available: bool
    model_installed: bool
    error_code: str | None = None
    message: str | None = None


class MediaProviderStatus(BaseModel):
    kind: Literal["image", "video"]
    provider: str
    configured: bool
    status: Literal["configured", "not_configured", "mock"]


class PipelineStatusResponse(BaseModel):
    text: AIStatusResponse
    jobs_mode: Literal["sync", "celery"]
    media: list[MediaProviderStatus]
    agents: list[str]
    agent_permissions: list[str]
    publishing_available: bool = Field(
        default=False, description="Always false: AI cannot publish in this system"
    )


class _GenBase(BaseModel):
    model_config = ConfigDict(extra="forbid")

    brand_profile_id: int | None = Field(
        default=None, description="Defaults to the default brand profile"
    )
    language: Language = "uz"
    instructions: str | None = Field(
        default=None,
        max_length=MAX_INSTRUCTIONS,
        description="Optional free-text request. Treated as untrusted data.",
    )


class StrategyRequest(_GenBase):
    goals: list[str] = Field(default_factory=list, max_length=10)


class IdeasRequest(_GenBase):
    count: int = Field(default=5, ge=1, le=10)
    formats: list[ContentType] | None = Field(default=None, max_length=4)
    topic: str | None = Field(default=None, max_length=300)
    save_as_drafts: bool = False


class ContentPlanRequest(_GenBase):
    start_date: date
    period: Literal["week", "month"] = "week"
    posts_per_week: int = Field(default=5, ge=1, le=7)
    save_as_drafts: bool = False


class _ContentGen(_GenBase):
    topic: str = Field(min_length=3, max_length=300)
    submit_for_review: bool = Field(
        default=False,
        description="If true and the quality check has no ERROR findings, the draft is moved "
        "to READY_FOR_REVIEW. It is never approved automatically.",
    )


class CaptionRequest(_ContentGen):
    pass


class CarouselRequest(_ContentGen):
    slides: int = Field(default=5, ge=MIN_CAROUSEL_SLIDES, le=MAX_CAROUSEL_SLIDES)


class ReelsRequest(_ContentGen):
    target_seconds: int = Field(default=30, ge=5, le=90)


class StoryRequest(_ContentGen):
    pass


class HashtagRequest(_GenBase):
    topic: str = Field(min_length=3, max_length=300)
    count: int = Field(default=15, ge=1, le=30)


class EvaluateRequest(BaseModel):
    """Evaluate a saved content item (``content_id``) or an unsaved draft (inline fields)."""

    model_config = ConfigDict(extra="forbid")

    content_id: int | None = None
    brand_profile_id: int | None = None
    content_type: ContentType | None = None
    language: Language = "uz"
    hook: str | None = Field(default=None, max_length=1000)
    caption: str | None = Field(default=None, max_length=5000)
    cta: str | None = Field(default=None, max_length=500)
    hashtags: list[str] = Field(default_factory=list, max_length=60)
    script: str | None = Field(default=None, max_length=10000)
    structure: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def _one_source(self) -> "EvaluateRequest":
        if self.content_id is None and self.content_type is None:
            raise ValueError("provide content_id or content_type with inline fields")
        return self


class ImageRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    content_id: int


class MediaResult(BaseModel):
    status: str
    provider: str
    model: str | None = None
    message: str | None = None
    error_code: str | None = None
    visual_prompt: str
    aspect_ratio: str
    assets_created: int = 0


class AIJobRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    job_type: str
    agent: str
    status: AIJobStatus
    provider: str | None
    model: str | None
    content_id: int | None
    created_at: datetime
    started_at: datetime | None
    finished_at: datetime | None
    duration_ms: int | None
    error_category: str | None
    error: str | None


class GenerationResponse(BaseModel):
    job: AIJobRead
    result: dict[str, Any] | None = Field(
        default=None, description="Validated AI output (null while queued or on failure)"
    )
    quality: QualityReport | None = None
    content_id: int | None = Field(
        default=None, description="Saved draft (status DRAFT or READY_FOR_REVIEW, never APPROVED)"
    )
    content_status: str | None = None
