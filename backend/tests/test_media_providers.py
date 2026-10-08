import pytest

from app.agents.visual import build_visual_prompt
from app.models.enums import ContentType
from app.providers.image.base import (
    ImageGenerationRequest,
    MediaStatus,
    MockImageProvider,
    NotConfiguredImageProvider,
)
from app.providers.media import create_image_provider, create_video_provider, recommend_crop
from app.providers.video.base import (
    MockVideoProvider,
    NotConfiguredVideoProvider,
    VideoGenerationRequest,
)


async def test_not_configured_providers_are_explicit():
    image = await NotConfiguredImageProvider().generate_image(ImageGenerationRequest(prompt="p"))
    video = await NotConfiguredVideoProvider().generate_video(VideoGenerationRequest(prompt="p"))
    for result in (image, video):
        assert result.status == MediaStatus.NOT_CONFIGURED
        assert result.error_code == "media_provider_not_configured"
        assert not result.has_real_media and result.media == []


async def test_mock_media_is_placeholder_not_success():
    image = await MockImageProvider().generate_image(ImageGenerationRequest(prompt="p"))
    video = await MockVideoProvider().generate_video(VideoGenerationRequest(prompt="p"))
    for result in (image, video):
        assert result.status == MediaStatus.PLACEHOLDER
        assert not result.has_real_media


def test_default_factories_are_not_configured():
    assert not create_image_provider().configured
    assert not create_video_provider().configured


def test_visual_prompt_uses_brand_and_format(brand):
    prompt = build_visual_prompt(brand, ContentType.REELS, "Small bedroom")
    assert "Small bedroom" in prompt and "Soft daylight" in prompt
    assert "aspect ratio 9:16" in prompt and "Reels" in prompt


@pytest.mark.parametrize(
    ("w", "h", "ctype", "valid", "ratio", "crop"),
    [
        (1080, 1350, ContentType.POST, True, "4:5", (1080, 1350)),
        (1080, 1080, ContentType.POST, True, "1:1", (1080, 1080)),
        (1920, 1080, ContentType.REELS, False, "9:16", (608, 1080)),
        (1080, 1920, ContentType.CAROUSEL, False, "4:5", (1080, 1350)),
    ],
)
def test_crop_recommendation(w, h, ctype, valid, ratio, crop):
    rec = recommend_crop(w, h, ctype)
    assert rec.valid is valid and rec.target_ratio == ratio
    assert (rec.crop_width, rec.crop_height) == crop
    assert rec.offset_x >= 0 and rec.offset_y >= 0
