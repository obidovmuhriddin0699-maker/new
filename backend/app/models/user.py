from sqlalchemy import BigInteger, Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, SoftDeleteMixin, TimestampMixin, str_enum
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

    instagram_accounts: Mapped[list["InstagramAccount"]] = relationship(  # noqa: F821
        back_populates="user"
    )
