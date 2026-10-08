"""Video generation interface (concrete providers arrive in a later phase)."""

from abc import ABC, abstractmethod

from app.providers.image.base import GeneratedMedia


class VideoProvider(ABC):
    name: str

    @abstractmethod
    async def generate_video(
        self, prompt: str, *, aspect_ratio: str = "9:16", duration_seconds: int = 15
    ) -> GeneratedMedia: ...
