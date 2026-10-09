"""Admin panel read models and brand / schedule request schemas."""

from datetime import date, datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.enums import ActorType, AssetKind


class UpcomingItem(BaseModel):
    content_id: int
    scheduled_at: datetime
    content_type: str
    topic: str | None


class DashboardSummaryRead(BaseModel):
    total: int
    by_status: dict[str, int]
    pending_approval: int
    scheduled: int
    published: int
    failed: int
    drafts: int
    reach: int | None = Field(description="From Meta insights only; null when no data")
    engagement_rate: float | None = Field(description="From Meta insights only; null when no data")
    analytics_available: bool
    upcoming: list[UpcomingItem]


class CalendarItemRead(BaseModel):
    content_id: int
    date: date
    at: datetime | None
    kind: Literal["scheduled", "published", "planned"]
    content_type: str
    status: str
    topic: str | None
    version: int


class CalendarRead(BaseModel):
    start: date
    end: date
    items: list[CalendarItemRead]


class AuditEventPanelRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    timestamp: datetime
    actor_type: ActorType
    actor_user_id: int | None
    actor_name: str | None
    action: str
    content_id: int | None
    content_version: int | None
    status: str
    error: str | None
    details: dict[str, Any]
    request_id: str | None


class AuditLogList(BaseModel):
    items: list[AuditEventPanelRead]
    total: int
    offset: int
    limit: int


class AssetListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    content_id: int
    kind: AssetKind
    position: int
    public_url: str | None
    mime_type: str | None
    width: int | None
    height: int | None
    duration_seconds: float | None
    provider: str | None
    created_at: datetime


class AssetList(BaseModel):
    items: list[AssetListItem]
    total: int


def _clean_list(value: list[str] | None) -> list[str] | None:
    if value is None:
        return None
    out = []
    for item in value:
        item = item.strip()
        if item and item not in out:
            if len(item) > 300:
                raise ValueError("list items must be at most 300 characters")
            out.append(item)
    return out


class BrandProfileRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    niche: str | None
    voice: list[str]
    topics: list[str]
    forbidden_rules: list[str]
    languages: list[str]
    visual_style: str | None
    target_audience: str | None
    services: list[str]
    preferred_styles: list[str]
    content_goals: list[str]
    preferred_ctas: list[str]
    banned_phrases: list[str]
    is_default: bool
    updated_at: datetime


class BrandProfileUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str | None = Field(default=None, min_length=2, max_length=120)
    niche: str | None = Field(default=None, max_length=120)
    voice: list[str] | None = Field(default=None, max_length=20)
    topics: list[str] | None = Field(default=None, max_length=50)
    forbidden_rules: list[str] | None = Field(default=None, max_length=30)
    languages: list[Literal["uz", "ru", "en"]] | None = Field(default=None, min_length=1)
    visual_style: str | None = Field(default=None, max_length=1500)
    target_audience: str | None = Field(default=None, max_length=1500)
    services: list[str] | None = Field(default=None, max_length=30)
    preferred_styles: list[str] | None = Field(default=None, max_length=20)
    content_goals: list[str] | None = Field(default=None, max_length=20)
    preferred_ctas: list[str] | None = Field(default=None, max_length=20)
    banned_phrases: list[str] | None = Field(default=None, max_length=50)

    _lists = field_validator(
        "voice",
        "topics",
        "forbidden_rules",
        "services",
        "preferred_styles",
        "content_goals",
        "preferred_ctas",
        "banned_phrases",
    )(_clean_list)


class BrandProfileCreate(BrandProfileUpdate):
    name: str = Field(min_length=2, max_length=120)
    make_default: bool = False


class ScheduleRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    scheduled_at: datetime = Field(description="Timezone-aware ISO datetime")


class ScheduleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    content_id: int
    content_version: int
    scheduled_at: datetime
    status: str
    created: bool = True
    note: str = "Scheduling does not publish yet: automatic publishing is implemented in PHASE 8."


class RegenerateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    content_id: int
    expected_version: int = Field(ge=1)
    instructions: str | None = Field(default=None, max_length=1000)
