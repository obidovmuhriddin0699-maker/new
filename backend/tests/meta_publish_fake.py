"""Stateful fake of the Content Publishing endpoints for unit tests (via respx).

Mirrors the documented behaviour: containers have a status_code; a container can be
published only once; content_publishing_limit returns quota_usage + config.
Failure injection lets tests simulate lost responses and Meta errors.
"""

import itertools
from dataclasses import dataclass, field
from typing import Any
from urllib.parse import parse_qs

import httpx

GRAPH = "https://graph.instagram.com"
VERSION = "v26.0"


@dataclass
class FakeContainer:
    id: str
    params: dict[str, str]
    statuses: list[str]  # popped on each status read; last one sticks
    published_media: str | None = None

    def status(self) -> str:
        if self.published_media:
            return "PUBLISHED"
        return self.statuses.pop(0) if len(self.statuses) > 1 else self.statuses[0]


@dataclass
class FakeMeta:
    ig_user_id: str
    quota_usage: int = 0
    quota_total: int | None = 100
    container_statuses: list[str] = field(default_factory=lambda: ["FINISHED"])
    # "ok" | "lost_after_publish" | "lost_before_publish" | "connect_error" | dict (error body)
    publish_behavior: Any = "ok"
    create_error: dict | None = None
    containers: dict[str, FakeContainer] = field(default_factory=dict)
    media: dict[str, dict[str, Any]] = field(default_factory=dict)
    requests: list[httpx.Request] = field(default_factory=list)
    publish_calls: int = 0
    _ids: Any = field(default_factory=lambda: itertools.count(1000))

    # ------------------------------------------------------------------ helpers
    @property
    def published(self) -> list[dict[str, Any]]:
        return list(self.media.values())

    def _err(self, status: int, body: dict) -> httpx.Response:
        return httpx.Response(status, json=body)

    # ------------------------------------------------------------------ handler
    def handler(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        path = request.url.path.strip("/").split("/")
        assert path[0] == VERSION, path
        rest = path[1:]
        if request.method == "POST":
            form = {k: v[0] for k, v in parse_qs(request.content.decode()).items()}
            assert form.get("access_token"), "token must be in the POST body"
            assert "access_token" not in str(request.url), "token must not be in the URL"
            if rest == [self.ig_user_id, "media"]:
                return self._create(form)
            if rest == [self.ig_user_id, "media_publish"]:
                return self._publish(form)
        if request.method == "GET":
            q = dict(request.url.params)
            assert q.get("access_token")
            if rest == [self.ig_user_id, "content_publishing_limit"]:
                config = {"quota_duration": 86400}
                if self.quota_total is not None:
                    config["quota_total"] = self.quota_total
                return httpx.Response(
                    200, json={"data": [{"quota_usage": self.quota_usage, "config": config}]}
                )
            if rest == [self.ig_user_id, "media"]:
                items = [
                    {"id": mid, **{k: m[k] for k in ("caption", "permalink", "timestamp")}}
                    for mid, m in reversed(self.media.items())
                ]
                return httpx.Response(200, json={"data": items})
            if len(rest) == 1 and rest[0] in self.containers:
                return httpx.Response(
                    200, json={"status_code": self.containers[rest[0]].status(), "id": rest[0]}
                )
            if len(rest) == 1 and rest[0] in self.media:
                m = self.media[rest[0]]
                return httpx.Response(200, json={"id": rest[0], "permalink": m["permalink"]})
        return self._err(
            400,
            {"error": {"message": "Unsupported request", "type": "OAuthException", "code": 100}},
        )

    def _create(self, form: dict[str, str]) -> httpx.Response:
        if self.create_error:
            return self._err(400, self.create_error)
        cid = str(next(self._ids))
        params = {k: v for k, v in form.items() if k != "access_token"}
        self.containers[cid] = FakeContainer(cid, params, list(self.container_statuses))
        return httpx.Response(200, json={"id": cid})

    def _publish(self, form: dict[str, str]) -> httpx.Response:
        self.publish_calls += 1
        behavior = self.publish_behavior
        if behavior == "connect_error":
            raise httpx.ConnectError("connection refused")
        if behavior == "lost_before_publish":
            self.publish_behavior = "ok"
            raise httpx.ReadTimeout("timed out")
        container = self.containers.get(form.get("creation_id", ""))
        if isinstance(behavior, dict):
            return self._err(400, behavior)
        if container is None:
            return self._err(
                400,
                {
                    "error": {
                        "message": "Invalid creation_id",
                        "type": "OAuthException",
                        "code": 100,
                    }
                },
            )
        if container.published_media:
            return self._err(
                400,
                {
                    "error": {
                        "message": "Media already published",
                        "code": 9004,
                        "error_subcode": 2207008,
                    }
                },
            )
        if container.status() != "FINISHED":
            return self._err(
                400,
                {"error": {"message": "Media not ready", "code": 9007, "error_subcode": 2207027}},
            )
        mid = f"1790{next(self._ids)}"
        container.published_media = mid
        self.media[mid] = {
            "caption": container.params.get("caption", ""),
            "permalink": f"https://www.instagram.com/p/{mid}/",
            "timestamp": "2026-10-09T10:00:00+0000",
            "container": container.id,
        }
        if behavior == "lost_after_publish":
            self.publish_behavior = "ok"
            raise httpx.ReadTimeout("timed out after publish")
        return httpx.Response(200, json={"id": mid})


def tiny_jpeg(width: int = 1080, height: int = 1350) -> bytes:
    """A minimal byte sequence our validator accepts as JPEG (SOI + SOF0 + EOI)."""
    sof = (
        b"\xff\xc0\x00\x11\x08"
        + height.to_bytes(2, "big")
        + width.to_bytes(2, "big")
        + b"\x03\x01\x22\x00\x02\x11\x01\x03\x11\x01"
    )
    return b"\xff\xd8" + sof + b"\x00" * 32 + b"\xff\xd9"


def tiny_mp4() -> bytes:
    return b"\x00\x00\x00\x18ftypmp42" + b"\x00" * 64
