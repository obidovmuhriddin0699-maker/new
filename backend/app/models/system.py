from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, str_enum, utcnow
from app.models.enums import ActorType, AIJobStatus


class AIJob(TimestampMixin, Base):
    __tablename__ = "ai_jobs"
    __table_args__ = (Index("ix_ai_jobs_status_created", "status", "created_at"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    agent: Mapped[str] = mapped_column(String(50))
    content_id: Mapped[int | None] = mapped_column(
        ForeignKey("contents.id", ondelete="SET NULL"), index=True
    )
    status: Mapped[AIJobStatus] = mapped_column(
        str_enum(AIJobStatus, 20), default=AIJobStatus.QUEUED
    )
    provider: Mapped[str | None] = mapped_column(String(50))
    model: Mapped[str | None] = mapped_column(String(100))
    input: Mapped[dict] = mapped_column(JSON, default=dict)
    output: Mapped[dict | None] = mapped_column(JSON)
    error: Mapped[str | None] = mapped_column(Text)
    duration_ms: Mapped[int | None] = mapped_column(Integer)


class AuditLog(Base):
    """Append-only audit trail (no updated_at, never soft-deleted)."""

    __tablename__ = "audit_logs"
    __table_args__ = (Index("ix_audit_logs_action_ts", "action", "timestamp"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )
    actor_type: Mapped[ActorType] = mapped_column(str_enum(ActorType, 10))
    actor_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), index=True
    )
    actor_name: Mapped[str | None] = mapped_column(String(100))  # agent name / system job
    action: Mapped[str] = mapped_column(String(100))
    content_id: Mapped[int | None] = mapped_column(
        ForeignKey("contents.id", ondelete="SET NULL"), index=True
    )
    status: Mapped[str] = mapped_column(String(30))
    error: Mapped[str | None] = mapped_column(Text)
    details: Mapped[dict] = mapped_column(JSON, default=dict)
    request_id: Mapped[str | None] = mapped_column(String(64))


class SystemSetting(TimestampMixin, Base):
    """Non-secret runtime settings. Secrets live in .env, never here."""

    __tablename__ = "system_settings"

    key: Mapped[str] = mapped_column(String(100), primary_key=True)
    value: Mapped[dict] = mapped_column(JSON, default=dict)
    description: Mapped[str | None] = mapped_column(Text)
