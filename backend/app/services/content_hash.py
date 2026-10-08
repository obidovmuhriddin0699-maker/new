"""Canonical snapshot + SHA-256 hash of a content version.

The hash covers everything that would be published or shapes what is
published (text fields, type, language, media references). Approvals store
this hash, so any change — even one that bypassed versioning — is detected.
"""

import hashlib
import json
from collections.abc import Iterable
from typing import Any

from app.models import Content, ContentAsset

VERSIONED_FIELDS: tuple[str, ...] = (
    "content_type",
    "language",
    "topic",
    "hook",
    "caption",
    "hashtags",
    "cta",
    "script",
    "visual_prompt",
    "aspect_ratio",
    "structure",
)


def media_snapshot(assets: Iterable[ContentAsset]) -> list[dict[str, Any]]:
    active = [a for a in assets if a.deleted_at is None]
    active.sort(key=lambda a: (a.position, a.id or 0))
    return [
        {
            "asset_id": a.id,
            "kind": a.kind.value if a.kind else None,
            "position": a.position,
            "storage_path": a.storage_path,
            "public_url": a.public_url,
            "mime_type": a.mime_type,
            "width": a.width,
            "height": a.height,
            "duration_seconds": a.duration_seconds,
            "checksum_sha256": a.checksum_sha256,
        }
        for a in active
    ]


def content_snapshot(content: Content, media: list[dict[str, Any]]) -> dict[str, Any]:
    snap: dict[str, Any] = {}
    for name in VERSIONED_FIELDS:
        value = getattr(content, name)
        snap[name] = value.value if hasattr(value, "value") else value
    snap["hashtags"] = list(snap.get("hashtags") or [])
    # Omitted when empty so versions created before ``structure`` existed keep their hash.
    if not snap.get("structure"):
        snap.pop("structure", None)
    snap["media"] = media
    return snap


def compute_hash(snapshot: dict[str, Any]) -> str:
    canonical = json.dumps(snapshot, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
