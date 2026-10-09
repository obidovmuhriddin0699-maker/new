from datetime import datetime

from sqlalchemy import JSON, BigInteger, ForeignKey, Index, Integer, String, Text, event
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UTCDateTime, str_enum, utcnow
from app.models.enums import ActorType, AIJobStatus


class AIJob(TimestampMixin, Base):
    __tablename__ = "ai_jobs"
    __table_args__ = (Index("ix_ai_jobs_status_created", "status", "created_at"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    agent: Mapped[str] = mapped_column(String(50))
    job_type: Mapped[str] = mapped_column(String(50), default="generic", index=True)
    created_by_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), index=True
    )
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
    error: Mapped[str | None] = mapped_column(Text)  # safe, user-presentable message only
    error_category: Mapped[str | None] = mapped_column(String(50))
    started_at: Mapped[datetime | None] = mapped_column(UTCDateTime())
    finished_at: Mapped[datetime | None] = mapped_column(UTCDateTime())
    duration_ms: Mapped[int | None] = mapped_column(Integer)


class AuditLog(Base):
    """Append-only audit trail (no updated_at, never soft-deleted)."""

    __tablename__ = "audit_logs"
    __table_args__ = (Index("ix_audit_logs_action_ts", "action", "timestamp"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    timestamp: Mapped[datetime] = mapped_column(UTCDateTime(), default=utcnow, nullable=False)
    actor_type: Mapped[ActorType] = mapped_column(str_enum(ActorType, 10))
    actor_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), index=True
    )
    actor_name: Mapped[str | None] = mapped_column(String(100))  # agent name / system job
    action: Mapped[str] = mapped_column(String(100))
    content_id: Mapped[int | None] = mapped_column(
        ForeignKey("contents.id", ondelete="SET NULL"), index=True
    )
    content_version: Mapped[int | None] = mapped_column(Integer)
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


class TelegramLinkCode(TimestampMixin, Base):
    """One-time code that links a Telegram account to a panel user (only the hash is stored)."""

    __tablename__ = "telegram_link_codes"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    code_hash: Mapped[str] = mapped_column(String(64), unique=True)
    expires_at: Mapped[datetime] = mapped_column(UTCDateTime())
    used_at: Mapped[datetime | None] = mapped_column(UTCDateTime())
    used_by_telegram_id: Mapped[int | None] = mapped_column(BigInteger)


class TelegramActionToken(TimestampMixin, Base):
    """One-time token behind an inline button.

    ``callback_data`` carries only a random token; the action, content id,
    content version and the Telegram user it was issued to live here, so a
    button cannot be forged, replayed, or used by another account.
    """

    __tablename__ = "telegram_action_tokens"
    __table_args__ = (Index("ix_telegram_action_tokens_content", "content_id", "content_version"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True)
    telegram_user_id: Mapped[int] = mapped_column(BigInteger, index=True)
    action: Mapped[str] = mapped_column(String(30))
    content_id: Mapped[int] = mapped_column(ForeignKey("contents.id", ondelete="CASCADE"))
    content_version: Mapped[int] = mapped_column(Integer)
    expires_at: Mapped[datetime] = mapped_column(UTCDateTime())
    used_at: Mapped[datetime | None] = mapped_column(UTCDateTime())


class OAuthState(TimestampMixin, Base):
    """One-time OAuth ``state`` (CSRF protection), bound to the user who started the flow."""

    __tablename__ = "oauth_states"

    id: Mapped[int] = mapped_column(primary_key=True)
    state_hash: Mapped[str] = mapped_column(String(64), unique=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    provider: Mapped[str] = mapped_column(String(30), default="instagram")
    expires_at: Mapped[datetime] = mapped_column(UTCDateTime())
    used_at: Mapped[datetime | None] = mapped_column(UTCDateTime())


class DataDeletionRequest(TimestampMixin, Base):
    """Meta data-deletion callback record (status page uses the confirmation code)."""

    __tablename__ = "data_deletion_requests"

    id: Mapped[int] = mapped_column(primary_key=True)
    confirmation_code: Mapped[str] = mapped_column(String(64), unique=True)
    platform_user_id: Mapped[str] = mapped_column(String(64), index=True)
    status: Mapped[str] = mapped_column(String(20), default="completed")
    details: Mapped[dict] = mapped_column(JSON, default=dict)


# ------------------------------------------------------------------ audit log is append-only
# Enforced by the database itself, so neither a bug nor a direct SQL session through the
# application's DB user can rewrite history. (A DB superuser can still drop the trigger;
# that is outside the application's trust boundary.)
AUDIT_APPEND_ONLY_SQL = {
    "postgresql": [
        """
        CREATE OR REPLACE FUNCTION audit_logs_append_only() RETURNS trigger AS $$
        BEGIN
            RAISE EXCEPTION 'audit_logs is append-only';
        END;
        $$ LANGUAGE plpgsql
        """,
        "CREATE TRIGGER audit_logs_no_update BEFORE UPDATE OR DELETE ON audit_logs "
        "FOR EACH ROW EXECUTE FUNCTION audit_logs_append_only()",
    ],
    "sqlite": [
        "CREATE TRIGGER audit_logs_no_update BEFORE UPDATE ON audit_logs "
        "BEGIN SELECT RAISE(ABORT, 'audit_logs is append-only'); END",
        "CREATE TRIGGER audit_logs_no_delete BEFORE DELETE ON audit_logs "
        "BEGIN SELECT RAISE(ABORT, 'audit_logs is append-only'); END",
    ],
}


def _install_audit_triggers(target, connection, **_kw) -> None:  # type: ignore[no-untyped-def]
    for statement in AUDIT_APPEND_ONLY_SQL.get(connection.dialect.name, []):
        connection.exec_driver_sql(statement)


event.listen(AuditLog.__table__, "after_create", _install_audit_triggers)
