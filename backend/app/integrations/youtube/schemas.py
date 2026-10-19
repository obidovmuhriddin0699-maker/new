"""Data schemas and types for YouTube Data API v3 integration."""

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class YouTubePrivacyStatus(StrEnum):
    PUBLIC = "public"
    PRIVATE = "private"
    UNLISTED = "unlisted"


class YouTubeCategory:
    FILM_ANIMATION = "1"
    AUTOS_VEHICLES = "2"
    MUSIC = "10"
    PETS_ANIMALS = "15"
    SPORTS = "17"
    GAMING = "20"
    PEOPLE_BLOGS = "22"
    COMEDY = "23"
    ENTERTAINMENT = "24"
    NEWS_POLITICS = "25"
    HOWTO_STYLE = "26"
    EDUCATION = "27"
    SCIENCE_TECHNOLOGY = "28"


class YouTubeAuthTokens(BaseModel):
    access_token: str
    refresh_token: str | None = None
    expires_in: int | None = 3600
    token_type: str = "Bearer"  # noqa: S105
    scope: str | None = None


class YouTubeVideoUploadRequest(BaseModel):
    title: str = Field(..., max_length=100, description="Video sarlavhasi")
    description: str = Field(default="", max_length=5000, description="Video tavsifi")
    tags: list[str] = Field(default_factory=list, description="Video teglari")
    category_id: str = Field(default=YouTubeCategory.PEOPLE_BLOGS, description="Kategoriya ID-si")
    privacy_status: YouTubePrivacyStatus = Field(
        default=YouTubePrivacyStatus.PRIVATE,
        description="Maxfiylik darajasi: public, private, unlisted",
    )
    publish_at: datetime | None = Field(
        default=None,
        description="Rejalashtirilgan vaqt (agar berilsa status 'private' bo'ladi)",
    )
    made_for_kids: bool = Field(default=False, description="Bolalar uchun mo'ljallanganmi")
    notify_subscribers: bool = Field(default=True, description="Obunachilarga bildirishnoma")


class YouTubeVideoResponse(BaseModel):
    video_id: str
    title: str
    description: str
    privacy_status: str
    publish_at: datetime | None = None
    url: str


class YouTubeVideoStats(BaseModel):
    video_id: str
    title: str
    view_count: int = 0
    like_count: int = 0
    comment_count: int = 0
    published_at: str | None = None
    privacy_status: str = "public"


class YouTubeChannelStats(BaseModel):
    channel_id: str
    title: str
    description: str
    custom_url: str | None = None
    subscriber_count: int = 0
    video_count: int = 0
    view_count: int = 0
