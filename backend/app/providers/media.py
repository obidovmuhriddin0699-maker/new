"""Media provider factory + format helpers (aspect ratios, crop recommendations)."""

from dataclasses import dataclass

from app.core.config import Settings, get_settings
from app.models.enums import ContentType
from app.providers.image.base import ImageProvider, MockImageProvider, NotConfiguredImageProvider
from app.providers.video.base import MockVideoProvider, NotConfiguredVideoProvider, VideoProvider

# Instagram formats used for validation. Re-verify against official Meta docs in PHASE 8.
ALLOWED_ASPECT_RATIOS: dict[ContentType, tuple[str, ...]] = {
    ContentType.POST: ("4:5", "1:1", "16:9"),
    ContentType.CAROUSEL: ("4:5", "1:1"),
    ContentType.REELS: ("9:16",),
    ContentType.STORY: ("9:16",),
}
DEFAULT_ASPECT_RATIO: dict[ContentType, str] = {
    ContentType.POST: "4:5",
    ContentType.CAROUSEL: "4:5",
    ContentType.REELS: "9:16",
    ContentType.STORY: "9:16",
}


def create_image_provider(settings: Settings | None = None) -> ImageProvider:
    settings = settings or get_settings()
    if settings.image_provider == "mock":
        return MockImageProvider()
    return NotConfiguredImageProvider()


def create_video_provider(settings: Settings | None = None) -> VideoProvider:
    settings = settings or get_settings()
    if settings.video_provider == "mock":
        return MockVideoProvider()
    return NotConfiguredVideoProvider()


def _ratio(value: str) -> float:
    w, h = value.split(":")
    return int(w) / int(h)


@dataclass(frozen=True, slots=True)
class CropRecommendation:
    valid: bool
    target_ratio: str
    crop_width: int
    crop_height: int
    offset_x: int
    offset_y: int
    message: str


def recommend_crop(width: int, height: int, content_type: ContentType) -> CropRecommendation:
    """Largest centred crop of (width x height) that matches an allowed ratio."""
    if width <= 0 or height <= 0:
        raise ValueError("width and height must be positive")
    allowed = ALLOWED_ASPECT_RATIOS[content_type]
    current = width / height
    for ratio in allowed:
        if abs(current - _ratio(ratio)) < 0.01:
            return CropRecommendation(True, ratio, width, height, 0, 0, "Format is valid.")
    target = min(allowed, key=lambda r: abs(_ratio(r) - current))
    t = _ratio(target)
    if current > t:  # too wide -> crop width
        cw, ch = round(height * t), height
    else:  # too tall -> crop height
        cw, ch = width, round(width / t)
    return CropRecommendation(
        False,
        target,
        cw,
        ch,
        (width - cw) // 2,
        (height - ch) // 2,
        f"Crop to {target} ({cw}x{ch}) for {content_type.value}.",
    )
