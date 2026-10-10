"""Image generation interface.

PHASE 3 ships no real image model. ``NotConfiguredImageProvider`` (the
default) answers every request with status ``not_configured`` and produces no
asset; ``MockImageProvider`` (tests/demos only) returns an explicitly marked
placeholder. Neither claims that a real image exists.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class MediaStatus(StrEnum):
    SUCCEEDED = "succeeded"  # a real file was produced by a real provider
    FAILED = "failed"
    TIMEOUT = "timeout"
    NOT_CONFIGURED = "not_configured"
    PLACEHOLDER = "placeholder"  # mock: metadata only, no real media


@dataclass(slots=True)
class GeneratedMedia:
    storage_path: str
    mime_type: str
    width: int | None = None
    height: int | None = None
    duration_seconds: float | None = None
    checksum_sha256: str | None = None


@dataclass(slots=True)
class ImageGenerationRequest:
    prompt: str
    aspect_ratio: str = "4:5"
    negative_prompt: str | None = None
    style: str | None = None
    seed: int | None = None
    count: int = 1


@dataclass(slots=True)
class MediaGenerationResult:
    status: MediaStatus
    provider: str
    model: str | None = None
    media: list[GeneratedMedia] = field(default_factory=list)
    error_code: str | None = None
    message: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def has_real_media(self) -> bool:
        return self.status == MediaStatus.SUCCEEDED and bool(self.media)


class ImageProvider(ABC):
    name: str
    model: str | None = None

    @abstractmethod
    async def generate_image(self, request: ImageGenerationRequest) -> MediaGenerationResult: ...

    @abstractmethod
    async def generate_variation(
        self, source_path: str, request: ImageGenerationRequest
    ) -> MediaGenerationResult: ...

    @property
    def configured(self) -> bool:
        return True


class NotConfiguredImageProvider(ImageProvider):
    name = "none"

    @property
    def configured(self) -> bool:
        return False

    async def generate_image(self, request: ImageGenerationRequest) -> MediaGenerationResult:
        return _not_configured(self.name, "image")

    async def generate_variation(
        self, source_path: str, request: ImageGenerationRequest
    ) -> MediaGenerationResult:
        return _not_configured(self.name, "image")


class MockImageProvider(ImageProvider):
    """Returns placeholder metadata only — never a file, never status SUCCEEDED."""

    name = "mock"
    model = "mock-image"

    async def generate_image(self, request: ImageGenerationRequest) -> MediaGenerationResult:
        return MediaGenerationResult(
            status=MediaStatus.PLACEHOLDER,
            provider=self.name,
            model=self.model,
            message="Mock provider: no image was generated.",
            metadata={"prompt_chars": len(request.prompt), "aspect_ratio": request.aspect_ratio},
        )

    async def generate_variation(
        self, source_path: str, request: ImageGenerationRequest
    ) -> MediaGenerationResult:
        return await self.generate_image(request)


def _not_configured(provider: str, kind: str) -> MediaGenerationResult:
    return MediaGenerationResult(
        status=MediaStatus.NOT_CONFIGURED,
        provider=provider,
        error_code="media_provider_not_configured",
        message=f"No {kind} generation provider is configured.",
    )
