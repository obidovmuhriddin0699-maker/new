from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import AssetKind
from app.schemas.content import ContentRead, PublishStateRead
from app.schemas.review import ReadinessRead


class PublishRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    expected_version: int = Field(ge=1, description="The approved version you are publishing")


class PublishStepRead(BaseModel):
    endpoint: str
    params: dict[str, str]
    note: str = ""


class PublishPlanRead(BaseModel):
    content_type: str
    version: int
    caption: str
    caption_length: int
    account_username: str | None
    steps: list[PublishStepRead]


class PublishPreviewRead(BaseModel):
    dry_run: bool
    ready: bool
    problems: list[str]
    readiness: ReadinessRead
    plan: PublishPlanRead | None


class PublishResponse(BaseModel):
    status: Literal[
        "dry_run", "queued", "published", "failed", "deferred", "in_progress", "skipped"
    ]
    message: str
    content: ContentRead | None
    publish_state: PublishStateRead | None = None
    preview: PublishPreviewRead | None = None


class AssetUrlRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    expected_version: int = Field(ge=1)
    kind: AssetKind
    public_url: str = Field(min_length=12, max_length=1000, pattern=r"^https://")
    position: int | None = Field(default=None, ge=0, le=20)
    mime_type: str | None = Field(default=None, max_length=100)


class PublishingLimitRead(BaseModel):
    instagram_account_id: int
    username: str | None
    quota_usage: int
    quota_total: int
    remaining: int
    quota_duration_seconds: int | None
    from_meta: bool


class CapabilityRead(BaseModel):
    key: str
    label: str
    supported: bool
    note: str
