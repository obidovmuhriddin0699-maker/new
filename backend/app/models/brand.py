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
    # Natural-language rules given to the model (prohibited claims/topics).
    forbidden_rules: Mapped[list[str]] = mapped_column(JSON, default=list)
    languages: Mapped[list[str]] = mapped_column(JSON, default=lambda: ["uz"])
    visual_style: Mapped[str | None] = mapped_column(Text)
    target_audience: Mapped[str | None] = mapped_column(Text)
    services: Mapped[list[str]] = mapped_column(JSON, default=list)
    preferred_styles: Mapped[list[str]] = mapped_column(JSON, default=list)
    content_goals: Mapped[list[str]] = mapped_column(JSON, default=list)
    preferred_ctas: Mapped[list[str]] = mapped_column(JSON, default=list)
    # Literal phrases the quality evaluator flags (e.g. "100% kafolat").
    banned_phrases: Mapped[list[str]] = mapped_column(JSON, default=list)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
