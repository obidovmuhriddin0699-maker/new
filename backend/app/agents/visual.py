"""Deterministic visual prompt builder (brand style + format aware)."""

from app.models import BrandProfile
from app.models.enums import ContentType
from app.providers.media import DEFAULT_ASPECT_RATIO

FORMAT_HINT = {
    ContentType.POST: "Instagram feed image",
    ContentType.CAROUSEL: "Instagram carousel slide background, space for text overlay",
    ContentType.REELS: "vertical video frame for Instagram Reels",
    ContentType.STORY: "vertical Instagram Story frame, space for text at top and bottom",
}


def build_visual_prompt(
    brand: BrandProfile,
    content_type: ContentType,
    topic: str,
    *,
    aspect_ratio: str | None = None,
    extra: str | None = None,
) -> str:
    ratio = aspect_ratio or DEFAULT_ASPECT_RATIO[content_type]
    parts = [
        topic.strip(),
        extra.strip() if extra else None,
        brand.visual_style,
        f"styles: {', '.join(brand.preferred_styles)}" if brand.preferred_styles else None,
        FORMAT_HINT[content_type],
        f"aspect ratio {ratio}",
        "photorealistic architectural visualization, no text, no logos, no people's faces",
    ]
    return ", ".join(p for p in parts if p)[:1500]
