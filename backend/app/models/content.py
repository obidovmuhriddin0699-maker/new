from datetime import datetime
from typing import Any

from sqlalchemy import (
    JSON,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import (
    Base,
    SoftDeleteMixin,
    TimestampMixin,
    UTCDateTime,
    str_enum,
    utcnow,
)
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
    """Working copy of a piece of content.

    ``version`` always points at the latest immutable ``ContentVersion`` row.
    There is deliberately no ``approved`` flag: whether content may be
    published is derived from an active ``Approval`` for exactly this version.
    """

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
    # Incremented on every content change; an approval is valid only for the version it saw.
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
    published_at: Mapped[datetime | None] = mapped_column(UTCDateTime())
    last_error: Mapped[str | None] = mapped_column(Text)

    assets: Mapped[list["ContentAsset"]] = relationship(
        back_populates="content", cascade="all, delete-orphan", order_by="ContentAsset.position"
    )
    versions: Mapped[list["ContentVersion"]] = relationship(
        back_populates="content", order_by="ContentVersion.version"
    )
    schedules: Mapped[list["ContentSchedule"]] = relationship(back_populates="content")
    approvals: Mapped[list["Approval"]] = relationship(back_populates="content")


class ContentVersion(Base):
    """Immutable snapshot of content at a given version (never updated)."""

    __tablename__ = "content_versions"
    __table_args__ = (UniqueConstraint("content_id", "version"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    content_id: Mapped[int] = mapped_column(
        ForeignKey("contents.id", ondelete="CASCADE"), index=True
    )
    version: Mapped[int] = mapped_column(Integer)
    content_type: Mapped[ContentType] = mapped_column(str_enum(ContentType, 20))
    language: Mapped[ContentLanguage] = mapped_column(str_enum(ContentLanguage, 5))
    topic: Mapped[str | None] = mapped_column(String(300))
    hook: Mapped[str | None] = mapped_column(Text)
    caption: Mapped[str | None] = mapped_column(Text)
    hashtags: Mapped[list[str]] = mapped_column(JSON, default=list)
    cta: Mapped[str | None] = mapped_column(Text)
    script: Mapped[str | None] = mapped_column(Text)
    visual_prompt: Mapped[str | None] = mapped_column(Text)
    aspect_ratio: Mapped[str | None] = mapped_column(String(10))
    # Snapshot of media references at this version (asset id, url, checksum, ...).
    media: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list)
    # Provider / model / ai_job_id / prompt info when the version was AI-generated.
    ai_metadata: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    source: Mapped[ActorType] = mapped_column(str_enum(ActorType, 10))
    created_by_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), index=True
    )
    created_by_name: Mapped[str | None] = mapped_column(String(100))  # agent / system name
    change_note: Mapped[str | None] = mapped_column(Text)
    # SHA-256 of the canonical snapshot; approvals bind to this exact value.
    content_hash: Mapped[str] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(UTCDateTime(), default=utcnow, nullable=False)

    content: Mapped[Content] = relationship(back_populates="versions")


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
    checksum_sha256: Mapped[str | None] = mapped_column(String(64))
    generation_prompt: Mapped[str | None] = mapped_column(Text)
    provider: Mapped[str | None] = mapped_column(String(50))

    content: Mapped[Content] = relationship(back_populates="assets")


class ContentSchedule(TimestampMixin, Base):
    """A planned (or immediate) publish of one approved content version."""

    __tablename__ = "content_schedules"
    __table_args__ = (Index("ix_content_schedules_status_at", "status", "scheduled_at"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    content_id: Mapped[int] = mapped_column(
        ForeignKey("contents.id", ondelete="CASCADE"), index=True
    )
    content_version: Mapped[int] = mapped_column(Integer)
    approval_id: Mapped[int] = mapped_column(
        ForeignKey("approvals.id", ondelete="RESTRICT"), index=True
    )
    created_by_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), index=True
    )
    scheduled_at: Mapped[datetime] = mapped_column(UTCDateTime())
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
    """A human decision on one exact content version.

    Only the ApprovalService (with a verified human actor) creates rows. An
    APPROVED row authorises publishing only while ``invalidated_at`` is NULL,
    ``content_version`` equals ``Content.version`` and ``content_hash`` equals
    the hash of that version's snapshot.
    """

    __tablename__ = "approvals"
    __table_args__ = (
        Index("ix_approvals_content_version", "content_id", "content_version"),
        # At most one *active* approval per content version (also the idempotency guard).
        Index(
            "uq_approvals_active_approved",
            "content_id",
            "content_version",
            unique=True,
            postgresql_where=text("decision = 'APPROVED' AND invalidated_at IS NULL"),
            sqlite_where=text("decision = 'APPROVED' AND invalidated_at IS NULL"),
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    content_id: Mapped[int] = mapped_column(
        ForeignKey("contents.id", ondelete="CASCADE"), index=True
    )
    content_version: Mapped[int] = mapped_column(Integer)
    content_hash: Mapped[str] = mapped_column(String(64))
    decision: Mapped[ApprovalDecision] = mapped_column(str_enum(ApprovalDecision, 20))
    decided_by_user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), index=True
    )
    channel: Mapped[ApprovalChannel] = mapped_column(str_enum(ApprovalChannel, 10))
    comment: Mapped[str | None] = mapped_column(Text)
    invalidated_at: Mapped[datetime | None] = mapped_column(UTCDateTime())
    invalidation_reason: Mapped[str | None] = mapped_column(String(200))

    content: Mapped[Content] = relationship(back_populates="approvals")

    @property
    def is_active_approval(self) -> bool:
        return self.decision == ApprovalDecision.APPROVED and self.invalidated_at is None


class ContentPerformance(TimestampMixin, Base):
    """Aggregated latest metrics per published content (only values Meta returned)."""

    __tablename__ = "content_performance"

    id: Mapped[int] = mapped_column(primary_key=True)
    content_id: Mapped[int] = mapped_column(
        ForeignKey("contents.id", ondelete="CASCADE"), unique=True
    )
    metrics: Mapped[dict] = mapped_column(JSON, default=dict)
    engagement_rate: Mapped[float | None] = mapped_column(Float)
    last_synced_at: Mapped[datetime | None] = mapped_column(UTCDateTime())
