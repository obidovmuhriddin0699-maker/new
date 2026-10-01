from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    email: Mapped[str] = mapped_column(String(254), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(256))


class Workspace(Base):
    __tablename__ = "workspaces"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(100))


class WorkspaceBilling(Base):
    __tablename__ = "workspace_billing"

    workspace_id: Mapped[str] = mapped_column(ForeignKey("workspaces.id"), primary_key=True)
    trial_started_at: Mapped[int] = mapped_column()
    trial_ends_at: Mapped[int] = mapped_column()
    status: Mapped[str] = mapped_column(String(16), default="trialing")
    plan_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    simulated_payment_id: Mapped[str | None] = mapped_column(String(64), nullable=True)


class WorkspaceUsage(Base):
    __tablename__ = "workspace_usage"
    __table_args__ = (UniqueConstraint("workspace_id", "metric", "period_start"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    workspace_id: Mapped[str] = mapped_column(ForeignKey("workspaces.id"), index=True)
    metric: Mapped[str] = mapped_column(String(64))
    period_start: Mapped[int] = mapped_column()
    units: Mapped[int] = mapped_column(default=0)


class Membership(Base):
    __tablename__ = "memberships"
    __table_args__ = (UniqueConstraint("workspace_id", "user_id"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    workspace_id: Mapped[str] = mapped_column(ForeignKey("workspaces.id"), index=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    role: Mapped[str] = mapped_column(String(10))


class AuthSession(Base):
    __tablename__ = "auth_sessions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    csrf_token_hash: Mapped[str] = mapped_column(String(64))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    active_workspace_id: Mapped[str | None] = mapped_column(
        ForeignKey("workspaces.id"), nullable=True
    )
    expires_at: Mapped[int] = mapped_column()
