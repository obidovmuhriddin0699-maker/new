from datetime import datetime

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, SoftDeleteMixin, TimestampMixin, UTCDateTime, str_enum
from app.models.enums import InstagramAccountType, MetaLoginMode


class InstagramAccount(TimestampMixin, SoftDeleteMixin, Base):
    """A connected Instagram professional account.

    SECURITY: no Instagram password field exists — connection is OAuth only.
    """

    __tablename__ = "instagram_accounts"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    # Instagram professional account id (``user_id`` from /me) — used for publishing.
    ig_user_id: Mapped[str] = mapped_column(String(64), unique=True)
    # App-scoped id (``id`` from /me / token exchange); Meta callbacks may reference it.
    ig_app_scoped_id: Mapped[str | None] = mapped_column(String(64), index=True)
    profile_picture_url: Mapped[str | None] = mapped_column(String(1000))
    username: Mapped[str | None] = mapped_column(String(100))
    account_type: Mapped[InstagramAccountType] = mapped_column(
        str_enum(InstagramAccountType, 20),
        default=InstagramAccountType.UNKNOWN,
    )
    login_mode: Mapped[MetaLoginMode] = mapped_column(
        str_enum(MetaLoginMode, 20), default=MetaLoginMode.INSTAGRAM
    )
    facebook_page_id: Mapped[str | None] = mapped_column(String(64))  # facebook mode only
    connected_at: Mapped[datetime | None] = mapped_column(UTCDateTime())

    user: Mapped["User"] = relationship(back_populates="instagram_accounts")  # noqa: F821
    tokens: Mapped[list["OAuthToken"]] = relationship(
        back_populates="instagram_account", cascade="all, delete-orphan"
    )


class OAuthToken(TimestampMixin, Base):
    """Encrypted OAuth access token. Plaintext is never persisted."""

    __tablename__ = "oauth_tokens"

    id: Mapped[int] = mapped_column(primary_key=True)
    instagram_account_id: Mapped[int] = mapped_column(
        ForeignKey("instagram_accounts.id", ondelete="CASCADE"), index=True
    )
    provider: Mapped[str] = mapped_column(String(30), default="meta")
    token_ciphertext: Mapped[str] = mapped_column(Text)  # Fernet ciphertext
    token_type: Mapped[str] = mapped_column(String(30), default="long_lived")
    scopes: Mapped[str | None] = mapped_column(Text)  # space-separated, as granted by Meta
    expires_at: Mapped[datetime | None] = mapped_column(UTCDateTime(), index=True)
    last_refreshed_at: Mapped[datetime | None] = mapped_column(UTCDateTime())
    revoked_at: Mapped[datetime | None] = mapped_column(UTCDateTime())

    instagram_account: Mapped[InstagramAccount] = relationship(back_populates="tokens")

    def __repr__(self) -> str:  # never include the ciphertext
        return f"<OAuthToken id={self.id} account={self.instagram_account_id}>"
