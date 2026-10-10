"""Insights client: Instagram API with Instagram Login (graph.instagram.com).

Checked against Meta's Insights documentation and changelogs (October 2026):

* Permission: ``instagram_business_manage_insights`` (plus ``instagram_business_basic``).
* ``impressions``, ``plays``, ``video_views`` and profile impressions were retired in 2025;
  ``views`` replaces them. They are never requested here.
* Media: ``GET /{version}/{ig-media-id}/insights?metric=...``. Supported metrics depend
  on ``media_product_type`` (FEED / REELS / STORY), and **one unsupported metric fails
  the whole request** (error #100 "incompatible metric"). The lists below are configurable
  per type, and on such an error each metric is requested on its own. Whatever Meta
  still refuses is reported as *unavailable*, never filled in.
* Account: ``GET /{version}/{ig-user-id}/insights?metric=...&period=day&metric_type=total_value
  &since=&until=`` (unix seconds; a window of at most 30 days). Without since/until Meta
  only looks back 24 hours.
* Followers / media count: ``GET /{version}/me?fields=followers_count,media_count``.

Response values arrive either as ``values[0].value`` or ``total_value.value``; both are read.
Tokens go in query parameters (Meta's convention); log redaction is installed for httpx.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

import httpx

from app.core.config import Settings, get_settings
from app.integrations.meta.errors import MetaApiError, MetaErrorKind, from_response

# Per media_product_type. Retired metrics (impressions, plays, video_views) are excluded.
MEDIA_METRICS: dict[str, tuple[str, ...]] = {
    "FEED": ("reach", "views", "likes", "comments", "shares", "saved", "total_interactions"),
    "REELS": ("reach", "views", "likes", "comments", "shares", "saved", "total_interactions"),
    "STORY": ("reach", "views", "shares", "total_interactions"),
}
MEDIA_FIELDS = "id,media_product_type,media_type,permalink,timestamp,like_count,comments_count"
ACCOUNT_METRICS: tuple[str, ...] = ("reach", "views", "accounts_engaged", "total_interactions")


@dataclass(slots=True)
class InsightsResult:
    metrics: dict[str, int | float] = field(default_factory=dict)
    unavailable: list[str] = field(default_factory=list)  # requested, not returned / refused


@dataclass(slots=True)
class MediaDetails:
    media_id: str
    media_product_type: str | None
    media_type: str | None
    permalink: str | None
    timestamp: str | None
    like_count: int | None = None
    comments_count: int | None = None


@dataclass(slots=True)
class ProfileCounts:
    followers_count: int | None
    media_count: int | None


class InstagramInsightsClient:
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

    # ------------------------------------------------------------------ media
    async def media_details(self, media_id: str) -> MediaDetails:
        data = await self._get(
            media_id,
            {"fields": MEDIA_FIELDS},
        )
        return MediaDetails(
            media_id=str(data.get("id") or media_id),
            media_product_type=data.get("media_product_type"),
            media_type=data.get("media_type"),
            permalink=data.get("permalink"),
            timestamp=data.get("timestamp"),
            like_count=_num(data.get("like_count")),
            comments_count=_num(data.get("comments_count")),
        )

    async def media_insights(self, media_id: str, product_type: str | None) -> InsightsResult:
        metrics = MEDIA_METRICS.get((product_type or "FEED").upper(), MEDIA_METRICS["FEED"])
        return await self._insights(f"{media_id}/insights", metrics, {})

    # ------------------------------------------------------------------ account
    async def account_insights(self, since: datetime, until: datetime) -> InsightsResult:
        params = {
            "period": "day",
            "metric_type": "total_value",
            "since": str(int(since.timestamp())),
            "until": str(int(until.timestamp())),
        }
        return await self._insights(f"{self.ig_user_id}/insights", ACCOUNT_METRICS, params)

    async def profile_counts(self) -> ProfileCounts:
        data = await self._get("me", {"fields": "followers_count,media_count"})
        return ProfileCounts(_num(data.get("followers_count")), _num(data.get("media_count")))

    # ------------------------------------------------------------------ internals
    async def _insights(
        self, path: str, metrics: tuple[str, ...], extra: dict[str, str]
    ) -> InsightsResult:
        try:
            data = await self._get(path, {**extra, "metric": ",".join(metrics)})
            result = _parse(data, metrics)
        except MetaApiError as exc:
            if exc.kind != MetaErrorKind.INVALID_REQUEST:
                raise
            # One incompatible metric fails the whole call: ask for each metric alone.
            result = InsightsResult()
            for metric in metrics:
                try:
                    single = _parse(await self._get(path, {**extra, "metric": metric}), (metric,))
                except MetaApiError as inner:
                    if inner.kind != MetaErrorKind.INVALID_REQUEST:
                        raise
                    result.unavailable.append(metric)
                    continue
                result.metrics.update(single.metrics)
                result.unavailable += single.unavailable
        return result

    async def _get(self, path: str, params: dict[str, str]) -> dict[str, Any]:
        try:
            resp = await self._client.get(
                self._url(path), params={**params, "access_token": self._token}
            )
        except httpx.TimeoutException as exc:
            raise MetaApiError(MetaErrorKind.NETWORK, meta_message="timeout") from exc
        except httpx.HTTPError as exc:
            raise MetaApiError(MetaErrorKind.NETWORK, meta_message=type(exc).__name__) from exc
        try:
            body = resp.json()
        except ValueError:
            body = None
        if resp.status_code >= 400 or not isinstance(body, dict) or "error" in body:
            raise from_response(resp.status_code, body)
        return body


def _parse(data: dict[str, Any], requested: tuple[str, ...]) -> InsightsResult:
    out = InsightsResult()
    for item in data.get("data") or []:
        if not isinstance(item, dict) or not item.get("name"):
            continue
        value: Any = None
        total = item.get("total_value")
        if isinstance(total, dict):
            value = total.get("value")
        elif item.get("values"):
            first = item["values"][0] if isinstance(item["values"], list) else None
            value = first.get("value") if isinstance(first, dict) else None
        number = _num(value)
        if number is not None:
            out.metrics[str(item["name"])] = number
    out.unavailable = [m for m in requested if m not in out.metrics]
    return out


def _num(value: Any) -> int | float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int | float):
        return value
    return None
