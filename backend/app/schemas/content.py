"""Content API schemas. Sensitive/internal fields are never exposed."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.enums import (
    ActorType,
    ApprovalChannel,
    ApprovalDecision,
    AssetKind,
    ContentLanguage,
    ContentStatus,
    ContentType,
)

# Instagram caption / hashtag limits. Re-verify against official Meta docs in PHASE 8.
MAX_CAPTION_LENGTH = 2200
MAX_HASHTAGS = 30
ASPECT_RATIO_PATTERN = r"^\d{1,2}:\d{1,2}$"


def _normalize_hashtags(value: list[str] | None) -> list[str] | None:
    if value is None:
        return None
    cleaned: list[str] = []
    for tag in value:
        tag = tag.strip()
        if not tag:
            continue
        if not tag.startswith("#"):
            tag = f"#{tag}"
        if " " in tag:
            raise ValueError(f"hashtag must not contain spaces: {tag!r}")
        if tag not in cleaned:
            cleaned.append(tag)
    return cleaned


class _ContentFields(BaseModel):
    topic: str | None = Field(default=None, max_length=300)
    hook: str | None = Field(default=None, max_length=1000)
    caption: str | None = Field(default=None, max_length=MAX_CAPTION_LENGTH)
    hashtags: list[str] | None = Field(default=None, max_length=MAX_HASHTAGS)
    cta: str | None = Field(default=None, max_length=500)
    script: str | None = Field(default=None, max_length=10000)
    visual_prompt: str | None = Field(default=None, max_length=4000)
    aspect_ratio: str | None = Field(default=None, pattern=ASPECT_RATIO_PATTERN)
    brand_profile_id: int | None = None
    instagram_account_id: int | None = None

    @field_validator("hashtags")
    @classmethod
    def _check_hashtags(cls, value: list[str] | None) -> list[str] | None:
        return _normalize_hashtags(value)


class ContentCreate(_ContentFields):
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "content_type": "CAROUSEL",
                "language": "uz",
                "topic": "Minimalist yotoqxona",
                "caption": "Minimalizm — bu bo‘shliq emas, balki to‘g‘ri tanlov.",
                "hashtags": ["#interiordesign", "#minimalism"],
                "cta": "Saqlab qo‘ying",
                "aspect_ratio": "4:5",
            }
        },
    )

    content_type: ContentType
    language: ContentLanguage = ContentLanguage.UZ


class ContentUpdate(_ContentFields):
    """Partial update. ``expected_version`` must equal the version you edited."""

    model_config = ConfigDict(extra="forbid")

    expected_version: int = Field(ge=1)
    content_type: ContentType | None = None
    language: ContentLanguage | None = None
    change_note: str | None = Field(default=None, max_length=500)

    def changes(self) -> dict[str, Any]:
        data = self.model_dump(exclude_unset=True, exclude={"expected_version", "change_note"})
        # Explicit null is allowed for optional text fields but not for the type/language.
        for required in ("content_type", "language"):
            if required in data and data[required] is None:
                data.pop(required)
        if "hashtags" in data and data["hashtags"] is None:
            data["hashtags"] = []
        return data


class DecisionRequest(BaseModel):
    """A human decision on the exact version shown to the reviewer."""

    model_config = ConfigDict(extra="forbid")

    expected_version: int = Field(ge=1, description="Version the reviewer saw")
    comment: str | None = Field(default=None, max_length=2000)


class AssetRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    kind: AssetKind
    position: int
    public_url: str | None
    mime_type: str | None
    width: int | None
    height: int | None
    duration_seconds: float | None
    checksum_sha256: str | None


class ApprovalRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    content_id: int
    content_version: int
    decision: ApprovalDecision
    decided_by_user_id: int
    channel: ApprovalChannel
    comment: str | None
    created_at: datetime
    invalidated_at: datetime | None
    invalidation_reason: str | None


class ContentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    content_type: ContentType
    status: ContentStatus
    version: int
    language: ContentLanguage
    topic: str | None
    hook: str | None
    caption: str | None
    hashtags: list[str]
    cta: str | None
    script: str | None
    visual_prompt: str | None
    aspect_ratio: str | None
    brand_profile_id: int | None
    instagram_account_id: int | None
    created_by: ActorType
    published_at: datetime | None
    ig_permalink: str | None
    last_error: str | None
    created_at: datetime
    updated_at: datetime
    assets: list[AssetRead] = []
    publish_authorized: bool = Field(
        default=False,
        description="True only if a valid human approval exists for the current version",
    )


class ContentList(BaseModel):
    items: list[ContentRead]
    total: int
    offset: int
    limit: int


class ApprovalResponse(BaseModel):
    content: ContentRead
    approval: ApprovalRead
    created: bool = Field(description="False when this exact approval already existed")


class ContentVersionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    version: int
    content_type: ContentType
    language: ContentLanguage
    topic: str | None
    hook: str | None
    caption: str | None
    hashtags: list[str]
    cta: str | None
    script: str | None
    visual_prompt: str | None
    aspect_ratio: str | None
    media: list[dict[str, Any]]
    ai_metadata: dict[str, Any]
    source: ActorType
    created_by_user_id: int | None
    created_by_name: str | None
    change_note: str | None
    content_hash: str
    created_at: datetime


class AuditEventRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    timestamp: datetime
    actor_type: ActorType
    actor_user_id: int | None
    actor_name: str | None
    action: str
    content_version: int | None
    status: str
    error: str | None
    details: dict[str, Any]


class ContentHistoryRead(BaseModel):
    content_id: int
    current_version: int
    status: ContentStatus
    versions: list[ContentVersionRead]
    approvals: list[ApprovalRead]
    events: list[AuditEventRead]
