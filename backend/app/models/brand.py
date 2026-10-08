from sqlalchemy import JSON, Boolean, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, SoftDeleteMixin, TimestampMixin


class BrandProfile(TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "brand_profiles"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True)
    niche: Mapped[str | None] = mapped_column(String(120))
    voice: Mapped[list[str]] = mapped_column(JSON, default=list)  # e.g. ["Premium", "Minimal"]
    topics: Mapped[list[str]] = mapped_column(JSON, default=list)
    forbidden_rules: Mapped[list[str]] = mapped_column(JSON, default=list)
    languages: Mapped[list[str]] = mapped_column(JSON, default=lambda: ["uz"])
    visual_style: Mapped[str | None] = mapped_column(Text)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
