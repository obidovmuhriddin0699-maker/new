"""Video generation interface (no real provider configured in PHASE 3)."""

from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.providers.image.base import MediaGenerationResult, MediaStatus, _not_configured


@dataclass(slots=True)
class VideoGenerationRequest:
    prompt: str
    aspect_ratio: str = "9:16"
    duration_seconds: int = 15


class VideoProvider(ABC):
    name: str
    model: str | None = None

    @abstractmethod
    async def generate_video(self, request: VideoGenerationRequest) -> MediaGenerationResult: ...

    @property
    def configured(self) -> bool:
        return True


class NotConfiguredVideoProvider(VideoProvider):
    name = "none"

    @property
    def configured(self) -> bool:
        return False

    async def generate_video(self, request: VideoGenerationRequest) -> MediaGenerationResult:
        return _not_configured(self.name, "video")


class MockVideoProvider(VideoProvider):
    name = "mock"
    model = "mock-video"

    async def generate_video(self, request: VideoGenerationRequest) -> MediaGenerationResult:
        return MediaGenerationResult(
            status=MediaStatus.PLACEHOLDER,
            provider=self.name,
            model=self.model,
            message="Mock provider: no video was generated.",
            metadata={"duration_seconds": request.duration_seconds},
        )
