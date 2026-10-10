"""What the Instagram Content Publishing API can and cannot do (October 2026).

The panel shows this matrix as-is. Anything marked unsupported is never faked:
the UI says "Not supported by current Meta API".
"""

from dataclasses import dataclass

from app.models.enums import ContentType, InstagramAccountType

NOT_SUPPORTED = "Not supported by current Meta API"


@dataclass(frozen=True, slots=True)
class Capability:
    key: str
    label: str
    supported: bool
    note: str


CAPABILITIES: tuple[Capability, ...] = (
    Capability("image_post", "Rasmli post", True, "JPEG, ochiq HTTPS URL"),
    Capability(
        "carousel", "Carousel", True, "2–10 ta rasm/video; birinchi rasm nisbati qo‘llanadi"
    ),
    Capability(
        "reels",
        "Reels",
        True,
        "Video ochiq HTTPS URL; qayta ishlash bir necha daqiqa olishi mumkin",
    ),
    Capability(
        "story", "Story", True, "Caption yo‘q; Creator akkauntlar uchun Meta hujjatlari aniq emas"
    ),
    Capability("scheduling", "Rejalashtirish", True, "Tizim o‘zi belgilangan vaqtda nashr qiladi"),
    Capability("music", "Musiqa qo‘shish", False, NOT_SUPPORTED),
    Capability("stickers", "Story stikerlari (link, so‘rovnoma, savol)", False, NOT_SUPPORTED),
    Capability("filters", "Instagram filtrlari va effektlar", False, NOT_SUPPORTED),
    Capability("drafts", "Instagram ilovasidagi qoralamalar", False, NOT_SUPPORTED),
    Capability("edit_after_publish", "Nashrdan keyin media almashtirish", False, NOT_SUPPORTED),
)


def account_warning(
    content_type: ContentType, account_type: InstagramAccountType | None
) -> str | None:
    """Meta's pages only clearly document Story publishing for Business accounts. We do
    not block Creator accounts (that would be guessing); Meta's own answer is shown."""
    if content_type == ContentType.STORY and account_type != InstagramAccountType.BUSINESS:
        return (
            "Story Creator akkauntdan nashr qilinmoqda: Meta hujjatlari buni aniq kafolatlamaydi. "
            "Meta rad etsa, xato matni ko‘rsatiladi."
        )
    return None
