from datetime import date, datetime
from typing import Any

from sqlalchemy import JSON, Date, ForeignKey, Index, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UTCDateTime, str_enum
from app.models.enums import ActorType


class AnalyticsSnapshot(TimestampMixin, Base):
    """Raw insights snapshot. ``metrics`` holds only what the Meta API actually returned;
    metrics that were requested but not returned are listed in ``unavailable``."""

    __tablename__ = "analytics_snapshots"
    __table_args__ = (
        Index("ix_analytics_snapshots_scope_captured", "scope", "captured_at"),
        Index(
            "ix_analytics_snapshots_account_period_end",
            "instagram_account_id",
            "period",
            "window_end",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    instagram_account_id: Mapped[int] = mapped_column(
        ForeignKey("instagram_accounts.id", ondelete="CASCADE"), index=True
    )
    content_id: Mapped[int | None] = mapped_column(
        ForeignKey("contents.id", ondelete="CASCADE"), index=True
    )
    scope: Mapped[str] = mapped_column(String(20))  # "account" | "media"
    # account: "day" | "week" | "days_28" (window_start..window_end); media: "lifetime"
    period: Mapped[str | None] = mapped_column(String(20))
    captured_at: Mapped[datetime] = mapped_column(UTCDateTime())
    window_start: Mapped[datetime | None] = mapped_column(UTCDateTime())
    window_end: Mapped[datetime | None] = mapped_column(UTCDateTime())
    ig_media_id: Mapped[str | None] = mapped_column(String(64), index=True)
    metrics: Mapped[dict] = mapped_column(JSON, default=dict)
    unavailable: Mapped[list[str]] = mapped_column(JSON, default=list, server_default=text("'[]'"))
    api_version: Mapped[str | None] = mapped_column(String(10))


class AnalyticsReport(TimestampMixin, Base):
    """Weekly analyst report. ``facts`` are computed from stored snapshots only; the AI
    may phrase them (``summary``/``highlights``/``recommendations``) but every number in
    its text must come from ``facts`` — otherwise the rule-based text is kept."""

    __tablename__ = "analytics_reports"
    __table_args__ = (Index("ix_analytics_reports_period", "period_start", "period_end"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    instagram_account_id: Mapped[int | None] = mapped_column(
        ForeignKey("instagram_accounts.id", ondelete="SET NULL"), index=True
    )
    period_start: Mapped[date] = mapped_column(Date)
    period_end: Mapped[date] = mapped_column(Date)  # inclusive
    status: Mapped[str] = mapped_column(String(20), default="READY")  # READY | NO_DATA
    facts: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    summary: Mapped[str] = mapped_column(Text, default="")
    highlights: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list)
    recommendations: Mapped[list[str]] = mapped_column(JSON, default=list)
    source: Mapped[str] = mapped_column(String(10), default="rules")  # "ai" | "rules"
    provider: Mapped[str | None] = mapped_column(String(50))
    model: Mapped[str | None] = mapped_column(String(100))
    ai_rejected_reason: Mapped[str | None] = mapped_column(Text)
    created_by: Mapped[ActorType] = mapped_column(str_enum(ActorType, 10))
    created_by_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), index=True
    )
