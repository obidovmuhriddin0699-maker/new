from datetime import datetime

from sqlalchemy import BigInteger, Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, SoftDeleteMixin, TimestampMixin, UTCDateTime, str_enum, utcnow
from app.models.enums import UserRole


class User(TimestampMixin, SoftDeleteMixin, Base):
    """A human operator of the system (the only actor allowed to approve)."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))  # Argon2 — app login only
    full_name: Mapped[str | None] = mapped_column(String(200))
    role: Mapped[UserRole] = mapped_column(str_enum(UserRole, 20), default=UserRole.OWNER)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    telegram_user_id: Mapped[int | None] = mapped_column(BigInteger, unique=True)
    # Tokens issued before this moment are rejected ("log out everywhere", password change).
    sessions_valid_after: Mapped[datetime | None] = mapped_column(UTCDateTime())
    password_changed_at: Mapped[datetime | None] = mapped_column(UTCDateTime())
    last_login_at: Mapped[datetime | None] = mapped_column(UTCDateTime())

    instagram_accounts: Mapped[list["InstagramAccount"]] = relationship(  # noqa: F821
        back_populates="user"
    )


class RevokedToken(Base):
    """Denylist of logged-out access tokens (by ``jti``) until they would expire anyway."""

    __tablename__ = "revoked_tokens"

    jti: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    expires_at: Mapped[datetime] = mapped_column(UTCDateTime(), index=True)
    revoked_at: Mapped[datetime] = mapped_column(UTCDateTime(), default=utcnow, nullable=False)
