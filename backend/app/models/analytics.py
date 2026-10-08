from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class AnalyticsSnapshot(TimestampMixin, Base):
    """Raw insights snapshot. ``metrics`` holds only what the Meta API actually returned."""

    __tablename__ = "analytics_snapshots"
    __table_args__ = (Index("ix_analytics_snapshots_scope_captured", "scope", "captured_at"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    instagram_account_id: Mapped[int] = mapped_column(
        ForeignKey("instagram_accounts.id", ondelete="CASCADE"), index=True
    )
    content_id: Mapped[int | None] = mapped_column(
        ForeignKey("contents.id", ondelete="CASCADE"), index=True
    )
    scope: Mapped[str] = mapped_column(String(20))  # "account" | "media"
    period: Mapped[str | None] = mapped_column(String(20))
    captured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    metrics: Mapped[dict] = mapped_column(JSON, default=dict)
    api_version: Mapped[str | None] = mapped_column(String(10))
