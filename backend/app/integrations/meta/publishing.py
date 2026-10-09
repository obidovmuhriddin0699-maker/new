"""Content Publishing client: Instagram API with Instagram Login (graph.instagram.com).

Checked against Meta's Content Publishing guide (October 2026):

* ``POST /{version}/{ig-user-id}/media`` creates a media **container**:
  - image post: ``image_url`` (+ ``caption``); JPEG is the safe, documented format.
  - Reels: ``media_type=REELS``, ``video_url`` (+ ``caption``, ``share_to_feed``).
  - Story: ``media_type=STORIES`` + ``image_url`` or ``video_url`` (no caption).
  - carousel item: ``is_carousel_item=true`` + ``image_url`` or ``media_type=VIDEO``
    + ``video_url``; then the carousel container: ``media_type=CAROUSEL``,
    ``children`` (comma-separated container ids, up to 10) + ``caption``.
* ``GET /{version}/{container-id}?fields=status_code``: ``IN_PROGRESS``, ``FINISHED``,
  ``PUBLISHED``, ``ERROR``, ``EXPIRED`` (not published within 24 hours).
* ``POST /{version}/{ig-user-id}/media_publish`` with ``creation_id`` → media id.
  If no media id comes back, the container's ``status_code`` tells whether it was
  published. A container can be published only once, so re-using the same container
  can never create a duplicate post.
* ``GET /{version}/{ig-user-id}/content_publishing_limit?fields=quota_usage,config``.
  Meta's pages disagree on the quota (50 vs 100 posts per 24 h), so the live
  ``config.quota_total`` is used and ``META_PUBLISH_LIMIT_FALLBACK`` only if it is missing.
* Meta downloads media from the given URL at publish time: it must be a public HTTPS URL.

Access tokens are sent in the form body for POST requests. Nothing here logs tokens.
"""

from dataclasses import dataclass
from enum import StrEnum
from typing import Any

import httpx

from app.core.config import Settings, get_settings
from app.integrations.meta.errors import MetaApiError, MetaErrorKind, from_response


class ContainerStatus(StrEnum):
    IN_PROGRESS = "IN_PROGRESS"
    FINISHED = "FINISHED"
    PUBLISHED = "PUBLISHED"
    ERROR = "ERROR"
    EXPIRED = "EXPIRED"
    UNKNOWN = "UNKNOWN"


class PublishOutcomeUnknownError(MetaApiError):
    """``media_publish`` was sent but no answer came back (timeout, dropped connection,
    5xx). The post may or may not be live: the caller must reconcile via the container
    status and must not create a new container."""

    def __init__(self, reason: str) -> None:
        super().__init__(MetaErrorKind.NETWORK, meta_message=f"publish outcome unknown: {reason}")
        self.code = "meta_publish_outcome_unknown"


@dataclass(slots=True)
class PublishingLimit:
    quota_usage: int
    quota_total: int
    quota_duration_seconds: int | None
    from_meta: bool  # False when quota_total came from the configured fallback

    @property
    def remaining(self) -> int:
        return max(self.quota_total - self.quota_usage, 0)


@dataclass(slots=True)
class MediaInfo:
    media_id: str
    permalink: str | None
    media_product_type: str | None
    timestamp: str | None
    caption: str | None = None


class InstagramPublishingClient:
    def __init__(
        self,
        access_token: str,
        ig_user_id: str,
        settings: Settings | None = None,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self.settings = settings or get_settings()
        self._token = access_token
        self.ig_user_id = ig_user_id
        self._client = client or httpx.AsyncClient(timeout=self.settings.meta_http_timeout_seconds)

    async def aclose(self) -> None:
        await self._client.aclose()

    def _url(self, path: str) -> str:
        s = self.settings
        return f"{s.meta_graph_base_url}/{s.meta_graph_api_version}/{path}"

    # ------------------------------------------------------------------ containers
    async def create_container(self, params: dict[str, str]) -> str:
        data = await self._request(
            "POST",
            self._url(f"{self.ig_user_id}/media"),
            data={**params, "access_token": self._token},
        )
        container_id = data.get("id")
        if not container_id:
            raise MetaApiError(MetaErrorKind.PUBLISHING_FAILED, meta_message="no container id")
        return str(container_id)

    async def container_status(self, container_id: str) -> ContainerStatus:
        data = await self._request(
            "GET",
            self._url(container_id),
            params={"fields": "status_code", "access_token": self._token},
        )
        try:
            return ContainerStatus(str(data.get("status_code") or "UNKNOWN"))
        except ValueError:
            return ContainerStatus.UNKNOWN

    # ------------------------------------------------------------------ publish
    async def publish(self, container_id: str) -> str:
        url = self._url(f"{self.ig_user_id}/media_publish")
        body = {"creation_id": container_id, "access_token": self._token}
        try:
            resp = await self._client.post(url, data=body)
        except (httpx.ConnectError, httpx.ConnectTimeout) as exc:
            # The request never reached Meta: nothing can have been published.
            raise MetaApiError(MetaErrorKind.NETWORK, meta_message=type(exc).__name__) from exc
        except httpx.HTTPError as exc:
            raise PublishOutcomeUnknownError(type(exc).__name__) from exc
        if resp.status_code >= 500:
            raise PublishOutcomeUnknownError(f"HTTP {resp.status_code}")
        payload = _json(resp)
        if resp.status_code >= 400 or not isinstance(payload, dict) or "error" in payload:
            raise from_response(resp.status_code, payload)
        media_id = payload.get("id")
        if not media_id:
            raise PublishOutcomeUnknownError("no media id in response")
        return str(media_id)

    # ------------------------------------------------------------------ reads
    async def publishing_limit(self) -> PublishingLimit:
        data = await self._request(
            "GET",
            self._url(f"{self.ig_user_id}/content_publishing_limit"),
            params={"fields": "quota_usage,config", "access_token": self._token},
        )
        entry = data.get("data", [data])
        entry = entry[0] if isinstance(entry, list) and entry else {}
        config = entry.get("config") or {}
        total = _int(config.get("quota_total"))
        return PublishingLimit(
            quota_usage=_int(entry.get("quota_usage")) or 0,
            quota_total=total if total is not None else self.settings.meta_publish_limit_fallback,
            quota_duration_seconds=_int(config.get("quota_duration")),
            from_meta=total is not None,
        )

    async def media_info(self, media_id: str) -> MediaInfo:
        data = await self._request(
            "GET",
            self._url(media_id),
            params={
                "fields": "id,permalink,media_product_type,timestamp",
                "access_token": self._token,
            },
        )
        return MediaInfo(
            media_id=str(data.get("id") or media_id),
            permalink=data.get("permalink"),
            media_product_type=data.get("media_product_type"),
            timestamp=data.get("timestamp"),
        )

    async def recent_media(self, limit: int = 10) -> list[MediaInfo]:
        data = await self._request(
            "GET",
            self._url(f"{self.ig_user_id}/media"),
            params={
                "fields": "id,caption,permalink,media_product_type,timestamp",
                "limit": str(limit),
                "access_token": self._token,
            },
        )
        items = data.get("data") or []
        return [
            MediaInfo(
                media_id=str(i.get("id")),
                permalink=i.get("permalink"),
                media_product_type=i.get("media_product_type"),
                timestamp=i.get("timestamp"),
                caption=i.get("caption"),
            )
            for i in items
            if isinstance(i, dict) and i.get("id")
        ]

    # ------------------------------------------------------------------ internals
    async def _request(self, method: str, url: str, **kwargs: Any) -> dict[str, Any]:
        try:
            resp = await self._client.request(method, url, **kwargs)
        except httpx.TimeoutException as exc:
            raise MetaApiError(MetaErrorKind.NETWORK, meta_message="timeout") from exc
        except httpx.HTTPError as exc:
            raise MetaApiError(MetaErrorKind.NETWORK, meta_message=type(exc).__name__) from exc
        body = _json(resp)
        if resp.status_code >= 400 or not isinstance(body, dict) or "error" in body:
            raise from_response(resp.status_code, body)
        return body


def _json(resp: httpx.Response) -> Any:
    try:
        return resp.json()
    except ValueError:
        return None


def _int(value: Any) -> int | None:
    try:
        return int(value) if value is not None else None
    except (TypeError, ValueError):
        return None
