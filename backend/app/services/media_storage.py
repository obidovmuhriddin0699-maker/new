"""Local media storage for publishing.

Meta downloads post media from a public HTTPS URL at publish time, so uploaded files
are stored under ``MEDIA_ROOT`` with a random, unguessable name and served (read-only)
at ``{MEDIA_PUBLIC_BASE_URL}/media/<name>``. Files are validated by their bytes, not
by the client's file name or Content-Type.

Accepted: JPEG images (the safe, documented format for the Content Publishing API) and
MP4/MOV videos.
"""

import hashlib
import re
import secrets
from dataclasses import dataclass
from pathlib import Path

from app.core.config import get_settings
from app.core.errors import AppError, NotFoundError
from app.models.enums import AssetKind

NAME_RE = re.compile(r"^[A-Za-z0-9_-]{20,64}\.(jpg|mp4|mov)$")
MIME = {"jpg": "image/jpeg", "mp4": "video/mp4", "mov": "video/quicktime"}


class MediaRejectedError(AppError):
    status_code = 422
    code = "media_rejected"


@dataclass(slots=True)
class StoredMedia:
    name: str
    kind: AssetKind
    mime_type: str
    size: int
    sha256: str
    width: int | None
    height: int | None
    public_url: str


def sniff(data: bytes) -> str | None:
    """Return the file extension by magic bytes, or None."""
    if data[:3] == b"\xff\xd8\xff":
        return "jpg"
    if len(data) >= 12 and data[4:8] == b"ftyp":
        brand = data[8:12]
        return "mov" if brand == b"qt  " else "mp4"
    return None


def jpeg_size(data: bytes) -> tuple[int, int] | None:
    """(width, height) from the first SOF marker; None if not found."""
    i = 2
    n = len(data)
    while i + 9 < n:
        if data[i] != 0xFF:
            i += 1
            continue
        marker = data[i + 1]
        if marker in (0xD8, 0x01) or 0xD0 <= marker <= 0xD7:
            i += 2
            continue
        length = int.from_bytes(data[i + 2 : i + 4], "big")
        if marker in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
            height = int.from_bytes(data[i + 5 : i + 7], "big")
            width = int.from_bytes(data[i + 7 : i + 9], "big")
            return (width, height) if width and height else None
        if length < 2:
            return None
        i += 2 + length
    return None


class MediaStorage:
    def __init__(self, root: str | Path | None = None) -> None:
        s = get_settings()
        self.root = Path(root or s.media_root)
        self.base_url = s.effective_media_base_url
        self.max_image = s.media_max_image_mb * 1024 * 1024
        self.max_video = s.media_max_video_mb * 1024 * 1024

    def save(self, data: bytes) -> StoredMedia:
        if not data:
            raise MediaRejectedError("Fayl bo‘sh.")
        ext = sniff(data)
        if ext is None:
            raise MediaRejectedError(
                "Faqat JPEG rasm yoki MP4/MOV video qabul qilinadi (fayl mazmuni tekshirildi)."
            )
        kind = AssetKind.IMAGE if ext == "jpg" else AssetKind.VIDEO
        limit = self.max_image if kind == AssetKind.IMAGE else self.max_video
        if len(data) > limit:
            raise MediaRejectedError(
                f"Fayl juda katta: {len(data) // (1024 * 1024)} MB "
                f"(chegara {limit // (1024 * 1024)} MB)."
            )
        width = height = None
        if kind == AssetKind.IMAGE:
            size = jpeg_size(data)
            if size is None:
                raise MediaRejectedError("JPEG fayl buzilgan yoki o‘lchamini aniqlab bo‘lmadi.")
            width, height = size
        name = f"{secrets.token_urlsafe(24)}.{ext}"
        self.root.mkdir(parents=True, exist_ok=True)
        path = self.root / name
        with open(path, "xb") as fh:  # never overwrite
            fh.write(data)
        return StoredMedia(
            name=name,
            kind=kind,
            mime_type=MIME[ext],
            size=len(data),
            sha256=hashlib.sha256(data).hexdigest(),
            width=width,
            height=height,
            public_url=f"{self.base_url}/media/{name}",
        )

    def path_for(self, name: str) -> Path:
        if not NAME_RE.fullmatch(name):
            raise NotFoundError("Media not found")
        path = self.root / name
        if not path.is_file():
            raise NotFoundError("Media not found")
        return path

    @staticmethod
    def mime_for(name: str) -> str:
        return MIME[name.rsplit(".", 1)[1]]
