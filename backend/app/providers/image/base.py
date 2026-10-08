"""Image generation interface (concrete providers arrive in a later phase)."""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(slots=True)
class GeneratedMedia:
    storage_path: str
    mime_type: str
    width: int | None = None
    height: int | None = None
    duration_seconds: float | None = None


class ImageProvider(ABC):
    name: str

    @abstractmethod
    async def generate_image(self, prompt: str, *, aspect_ratio: str) -> GeneratedMedia: ...

    @abstractmethod
    async def generate_variation(self, source_path: str, *, prompt: str) -> GeneratedMedia: ...
