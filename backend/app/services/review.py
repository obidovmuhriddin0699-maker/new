"""Review helpers for approvers: publish readiness (preflight) and version diffs.

``readiness`` is a read-only checklist. The publish service calls it (together with
``ApprovalService.require_valid_approval``) before contacting Meta, so the panel and
the publisher share exactly the same rules.
"""

import difflib
import json
from dataclasses import dataclass
from typing import Any, Literal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.agents.quality import EvaluationInput, QualityEvaluator
from app.core.config import get_settings
from app.core.errors import AppError, NotFoundError
from app.integrations.meta.capabilities import account_warning
from app.models import Content, ContentAsset, ContentVersion, InstagramAccount
from app.models.base import utcnow
from app.models.enums import ApprovalDecision, AssetKind, ContentStatus, ContentType
from app.providers.media import ALLOWED_ASPECT_RATIOS
from app.repositories import (
    ApprovalRepository,
    BrandProfileRepository,
    ContentAssetRepository,
    ContentRepository,
    ContentVersionRepository,
    OAuthTokenRepository,
)
from app.services.approval import APPROVAL_REASON_TEXT, ApprovalService

PUBLISH_SCOPE = "instagram_business_content_publish"


def _status_hint(status: ContentStatus) -> str:
    if status in PUBLISHABLE_STATUSES:
        return ""
    if status == ContentStatus.PUBLISHED:
        return " — allaqachon nashr qilingan"
    if status == ContentStatus.PUBLISHING:
        return " — nashr jarayonda"
    return " — avval tasdiqlash kerak"


def _is_jpeg(asset: ContentAsset) -> bool:
    if asset.mime_type:
        return asset.mime_type.lower() in ("image/jpeg", "image/jpg")
    path = (asset.public_url or "").split("?", 1)[0].lower()
    return path.endswith((".jpg", ".jpeg"))


Severity = Literal["blocker", "warning", "info"]
PUBLISHABLE_STATUSES = (ContentStatus.APPROVED, ContentStatus.SCHEDULED, ContentStatus.FAILED)
REQUIRED_MEDIA: dict[ContentType, tuple[set[AssetKind], int, int]] = {
    # kinds allowed, min count, max count
    ContentType.POST: ({AssetKind.IMAGE}, 1, 1),
    ContentType.CAROUSEL: ({AssetKind.IMAGE, AssetKind.VIDEO}, 2, 10),
    ContentType.REELS: ({AssetKind.VIDEO}, 1, 1),
    ContentType.STORY: ({AssetKind.IMAGE, AssetKind.VIDEO}, 1, 1),
}


@dataclass(slots=True)
class ReadinessCheck:
    key: str
    ok: bool
    severity: Severity
    message: str


@dataclass(slots=True)
class Readiness:
    ready: bool
    content_id: int
    version: int
    checks: list[ReadinessCheck]


@dataclass(slots=True)
class FieldDiff:
    field: str
    changed: bool
    old: Any
    new: Any
    lines: list[dict[str, str]]  # [{"op": "equal|add|remove", "text": ...}] for text fields


@dataclass(slots=True)
class VersionDiff:
    content_id: int
    from_version: int
    to_version: int
    from_label: str
    fields: list[FieldDiff]

    @property
    def changed_fields(self) -> list[str]:
        return [f.field for f in self.fields if f.changed]


TEXT_FIELDS = ("topic", "hook", "caption", "cta", "script", "visual_prompt")
SCALAR_FIELDS = ("content_type", "language", "aspect_ratio")


class ReviewService:
    def __init__(self, session: Session) -> None:
        self.session = session

    # ------------------------------------------------------------------ readiness
    def readiness(self, content_id: int) -> Readiness:
        content = ContentRepository(self.session).get(content_id)
        if content is None:
            raise NotFoundError("Content not found")
        checks: list[ReadinessCheck] = []

        def add(key: str, ok: bool, message: str, severity: Severity = "blocker") -> None:
            checks.append(ReadinessCheck(key, ok, severity, message))

        add(
            "status",
            content.status in PUBLISHABLE_STATUSES,
            f"Holat: {content.status.value}" + _status_hint(content.status),
        )
        check = ApprovalService(self.session).evaluate(content)
        add(
            "approval",
            check.valid,
            f"v{content.version} inson tomonidan tasdiqlangan"
            if check.valid
            else " ".join(APPROVAL_REASON_TEXT.get(r, r) for r in check.reasons),
        )

        brand = (
            BrandProfileRepository(self.session).get(content.brand_profile_id)
            if content.brand_profile_id
            else None
        )
        report = QualityEvaluator(brand).evaluate(EvaluationInput.from_content(content))
        errors = [f for f in report.findings if f.severity.value == "ERROR"]
        add(
            "quality",
            not errors,
            "Sifat tekshiruvida xato yo‘q"
            if not errors
            else "Sifat xatolari: " + ", ".join(f.code for f in errors),
        )

        ratios = ALLOWED_ASPECT_RATIOS[content.content_type]
        add(
            "format",
            content.aspect_ratio in ratios,
            f"Format {content.aspect_ratio or '—'} ({content.content_type.value} uchun: "
            f"{', '.join(ratios)})",
        )

        kinds, min_n, max_n = REQUIRED_MEDIA[content.content_type]
        assets = ContentAssetRepository(self.session).list_for_content(content.id)
        usable = [a for a in assets if a.public_url and a.kind in kinds]
        media_ok = min_n <= len(usable) <= max_n and len(usable) == len(assets)
        add(
            "media",
            media_ok,
            f"Media: {len(usable)}/{len(assets)} ta ochiq URL bilan "
            f"(kerak: {min_n}–{max_n}, {'/'.join(k.value for k in kinds)})"
            if assets
            else "Media yo‘q — rasm/video provayderi sozlanmagan yoki fayl yuklanmagan",
        )
        bad_urls = [a.id for a in usable if not (a.public_url or "").startswith("https://")]
        if usable:
            add(
                "media_https",
                not bad_urls,
                "Barcha media HTTPS orqali ochiq"
                if not bad_urls
                else f"HTTPS bo‘lmagan media: {bad_urls} (Meta media’ni HTTPS URL orqali oladi)",
            )
            not_jpeg = [a.id for a in usable if a.kind == AssetKind.IMAGE and not _is_jpeg(a)]
            if any(a.kind == AssetKind.IMAGE for a in usable):
                add(
                    "media_format",
                    not not_jpeg,
                    "Rasmlar JPEG formatida"
                    if not not_jpeg
                    else f"JPEG bo‘lmagan rasm: {not_jpeg} "
                    "(Meta faqat JPEG’ni ishonchli qabul qiladi)",
                )

        account = self.publish_account(content)
        add(
            "instagram_account",
            account is not None,
            f"Instagram akkaunt: @{account.username or account.ig_user_id}, token amalda"
            if account is not None
            else self._account_problem(content),
        )
        if account is not None:
            token = OAuthTokenRepository(self.session).get_active_for_account(account.id)
            scopes = set(((token.scopes if token else None) or "").replace(",", " ").split())
            add(
                "publish_permission",
                PUBLISH_SCOPE in scopes,
                f"{PUBLISH_SCOPE} ruxsati berilgan"
                if PUBLISH_SCOPE in scopes
                else f"{PUBLISH_SCOPE} ruxsati yo‘q — akkauntni qayta ulang",
            )
            warning = account_warning(content.content_type, account.account_type)
            if warning:
                add("account_type", False, warning, "warning")

        if get_settings().meta_dry_run:
            add(
                "dry_run",
                False,
                "META_DRY_RUN=true — tekshiruv va reja ko‘rsatiladi, Instagram’ga hech narsa "
                "yuborilmaydi",
                "warning",
            )
        else:
            add("publisher", True, "Nashr servisi tayyor (rasmiy Meta Content Publishing API)")

        ready = all(c.ok for c in checks if c.severity == "blocker")
        return Readiness(ready=ready, content_id=content.id, version=content.version, checks=checks)

    def publish_account(self, content: Content) -> InstagramAccount | None:
        """The account this content will be published to: the one set on the content,
        else the only connected account. Requires a live (unexpired) token."""
        stmt = select(InstagramAccount).where(InstagramAccount.deleted_at.is_(None))
        if content.instagram_account_id:
            stmt = stmt.where(InstagramAccount.id == content.instagram_account_id)
        accounts = [a for a in self.session.scalars(stmt) if self._token_live(a)]
        return accounts[0] if len(accounts) == 1 else None

    def _account_problem(self, content: Content) -> str:
        live = [
            a
            for a in self.session.scalars(
                select(InstagramAccount).where(InstagramAccount.deleted_at.is_(None))
            )
            if self._token_live(a)
        ]
        if not content.instagram_account_id and len(live) > 1:
            return "Bir nechta Instagram akkaunt ulangan — kontent uchun akkauntni tanlang"
        return "Instagram akkaunt ulanmagan yoki tokenni yangilash kerak (Instagram sahifasi)"

    def _token_live(self, account: InstagramAccount) -> bool:
        token = OAuthTokenRepository(self.session).get_active_for_account(account.id)
        return token is not None and (token.expires_at is None or token.expires_at > utcnow())

    # ------------------------------------------------------------------ diff
    def default_base_version(self, content: Content) -> tuple[int, str]:
        """Compare against the last approved version if older, else the previous one."""
        approved = [
            a.content_version
            for a in ApprovalRepository(self.session).list_for_content(content.id)
            if a.decision == ApprovalDecision.APPROVED and a.content_version < content.version
        ]
        if approved:
            return max(approved), "oxirgi tasdiqlangan versiya"
        return max(1, content.version - 1), "oldingi versiya"

    def diff(
        self, content_id: int, from_version: int | None = None, to_version: int | None = None
    ) -> VersionDiff:
        content = ContentRepository(self.session).get(content_id)
        if content is None:
            raise NotFoundError("Content not found")
        to_v = to_version or content.version
        label = "tanlangan versiya"
        if from_version is None:
            from_version, label = self.default_base_version(content)
        versions = ContentVersionRepository(self.session)
        old = versions.get_version(content.id, from_version)
        new = versions.get_version(content.id, to_v)
        if old is None or new is None:
            raise AppError("Unknown version number", code="invalid_version")
        fields: list[FieldDiff] = []
        for name in TEXT_FIELDS:
            a, b = getattr(old, name) or "", getattr(new, name) or ""
            fields.append(
                FieldDiff(name, a != b, a or None, b or None, _line_diff(a, b) if a != b else [])
            )
        for name in SCALAR_FIELDS:
            a, b = _scalar(getattr(old, name)), _scalar(getattr(new, name))
            fields.append(FieldDiff(name, a != b, a, b, []))
        a_tags, b_tags = list(old.hashtags or []), list(new.hashtags or [])
        fields.append(
            FieldDiff(
                "hashtags",
                a_tags != b_tags,
                a_tags,
                b_tags,
                [{"op": "remove", "text": t} for t in a_tags if t not in b_tags]
                + [{"op": "add", "text": t} for t in b_tags if t not in a_tags],
            )
        )
        for name in ("structure", "media"):
            a_obj, b_obj = getattr(old, name) or {}, getattr(new, name) or {}
            a_txt, b_txt = _pretty(a_obj), _pretty(b_obj)
            fields.append(
                FieldDiff(
                    name,
                    a_obj != b_obj,
                    a_obj or None,
                    b_obj or None,
                    _line_diff(a_txt, b_txt) if a_obj != b_obj else [],
                )
            )
        return VersionDiff(content.id, from_version, to_v, label, fields)


def _scalar(value: Any) -> Any:
    return value.value if hasattr(value, "value") else value


def _pretty(obj: Any) -> str:
    if not obj:
        return ""
    return json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=True)


def _line_diff(a: str, b: str) -> list[dict[str, str]]:
    out = []
    for line in difflib.ndiff(a.splitlines(), b.splitlines()):
        tag, text = line[:2], line[2:]
        if tag == "  ":
            out.append({"op": "equal", "text": text})
        elif tag == "- ":
            out.append({"op": "remove", "text": text})
        elif tag == "+ ":
            out.append({"op": "add", "text": text})
    return out


__all__ = ["ContentVersion", "Readiness", "ReviewService", "VersionDiff"]
