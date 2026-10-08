from datetime import datetime

from sqlalchemy import (
    JSON,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, SoftDeleteMixin, TimestampMixin, str_enum
from app.models.enums import (
    ActorType,
    ApprovalChannel,
    ApprovalDecision,
    AssetKind,
    ContentLanguage,
    ContentStatus,
    ContentType,
    ScheduleStatus,
)


class Content(TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "contents"
    __table_args__ = (Index("ix_contents_status_created", "status", "created_at"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    instagram_account_id: Mapped[int | None] = mapped_column(
        ForeignKey("instagram_accounts.id", ondelete="SET NULL"), index=True
    )
    brand_profile_id: Mapped[int | None] = mapped_column(
        ForeignKey("brand_profiles.id", ondelete="SET NULL"), index=True
    )
    content_type: Mapped[ContentType] = mapped_column(str_enum(ContentType, 20))
    status: Mapped[ContentStatus] = mapped_column(
        str_enum(ContentStatus, 30), default=ContentStatus.DRAFT
    )
    # Incremented on every edit; an approval is valid only for the version it saw.
    version: Mapped[int] = mapped_column(Integer, default=1)
    language: Mapped[ContentLanguage] = mapped_column(
        str_enum(ContentLanguage, 5), default=ContentLanguage.UZ
    )
    topic: Mapped[str | None] = mapped_column(String(300))
    hook: Mapped[str | None] = mapped_column(Text)
    caption: Mapped[str | None] = mapped_column(Text)
    hashtags: Mapped[list[str]] = mapped_column(JSON, default=list)
    cta: Mapped[str | None] = mapped_column(Text)
    script: Mapped[str | None] = mapped_column(Text)  # Reels / Story script
    visual_prompt: Mapped[str | None] = mapped_column(Text)
    aspect_ratio: Mapped[str | None] = mapped_column(String(10))
    created_by: Mapped[ActorType] = mapped_column(str_enum(ActorType, 10), default=ActorType.AGENT)
    ig_media_id: Mapped[str | None] = mapped_column(String(64), unique=True)
    ig_permalink: Mapped[str | None] = mapped_column(String(500))
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_error: Mapped[str | None] = mapped_column(Text)

    assets: Mapped[list["ContentAsset"]] = relationship(
        back_populates="content", cascade="all, delete-orphan", order_by="ContentAsset.position"
    )
    schedules: Mapped[list["ContentSchedule"]] = relationship(back_populates="content")
    approvals: Mapped[list["Approval"]] = relationship(back_populates="content")


class ContentAsset(TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "content_assets"

    id: Mapped[int] = mapped_column(primary_key=True)
    content_id: Mapped[int] = mapped_column(
        ForeignKey("contents.id", ondelete="CASCADE"), index=True
    )
    kind: Mapped[AssetKind] = mapped_column(str_enum(AssetKind, 10))
    position: Mapped[int] = mapped_column(Integer, default=0)  # carousel order
    storage_path: Mapped[str | None] = mapped_column(String(500))
    public_url: Mapped[str | None] = mapped_column(String(1000))  # Meta fetches media by URL
    mime_type: Mapped[str | None] = mapped_column(String(100))
    width: Mapped[int | None] = mapped_column(Integer)
    height: Mapped[int | None] = mapped_column(Integer)
    duration_seconds: Mapped[float | None] = mapped_column(Float)
    generation_prompt: Mapped[str | None] = mapped_column(Text)
    provider: Mapped[str | None] = mapped_column(String(50))

    content: Mapped[Content] = relationship(back_populates="assets")


class ContentSchedule(TimestampMixin, Base):
    __tablename__ = "content_schedules"
    __table_args__ = (Index("ix_content_schedules_status_at", "status", "scheduled_at"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    content_id: Mapped[int] = mapped_column(
        ForeignKey("contents.id", ondelete="CASCADE"), index=True
    )
    scheduled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    status: Mapped[ScheduleStatus] = mapped_column(
        str_enum(ScheduleStatus, 20), default=ScheduleStatus.PENDING
    )
    # Prevents duplicate posts on retry: one publish per content version.
    idempotency_key: Mapped[str] = mapped_column(String(128), unique=True)
    ig_container_id: Mapped[str | None] = mapped_column(String(64))
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    last_error: Mapped[str | None] = mapped_column(Text)

    content: Mapped[Content] = relationship(back_populates="schedules")


class Approval(TimestampMixin, Base):
    """A human decision on a specific content version. Agents cannot create APPROVED rows."""

    __tablename__ = "approvals"
    __table_args__ = (UniqueConstraint("content_id", "content_version", "decision"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    content_id: Mapped[int] = mapped_column(
        ForeignKey("contents.id", ondelete="CASCADE"), index=True
    )
    content_version: Mapped[int] = mapped_column(Integer)
    decision: Mapped[ApprovalDecision] = mapped_column(str_enum(ApprovalDecision, 20))
    decided_by_user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), index=True
    )
    channel: Mapped[ApprovalChannel] = mapped_column(str_enum(ApprovalChannel, 10))
    comment: Mapped[str | None] = mapped_column(Text)

    content: Mapped[Content] = relationship(back_populates="approvals")


class ContentPerformance(TimestampMixin, Base):
    """Aggregated latest metrics per published content (only values Meta returned)."""

    __tablename__ = "content_performance"

    id: Mapped[int] = mapped_column(primary_key=True)
    content_id: Mapped[int] = mapped_column(
        ForeignKey("contents.id", ondelete="CASCADE"), unique=True
    )
    metrics: Mapped[dict] = mapped_column(JSON, default=dict)
    engagement_rate: Mapped[float | None] = mapped_column(Float)
    last_synced_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
