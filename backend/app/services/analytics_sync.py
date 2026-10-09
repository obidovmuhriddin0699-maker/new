"""Insights sync: Meta → ``analytics_snapshots`` / ``content_performance``.

Read-only towards Instagram. Only values Meta returned are stored; metrics it did not
return are recorded in ``unavailable`` and shown as "—" — never estimated.

* Account windows end at the start of the current UTC day (complete days only):
  ``day`` (1 day), ``week`` (7 days), ``days_28`` (28 days). Stored once per window end,
  so running the sync several times a day does not duplicate rows.
* Media: content published by this system within ``ANALYTICS_MEDIA_DAYS``; a lifetime
  snapshot per run (growth history) and the latest values in ``content_performance``.
* ``engagement_rate`` is *our* ratio ``total_interactions / reach`` — only when Meta
  returned both. Instagram has no official "engagement rate" metric.
"""

import logging
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime, time, timedelta
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.agents.structured import run_sync
from app.core.actors import SystemActor
from app.core.config import get_settings
from app.core.transaction import atomic
from app.integrations.meta.errors import MetaApiError
from app.integrations.meta.insights import InsightsResult, InstagramInsightsClient
from app.models import AnalyticsSnapshot, Content, ContentPerformance, InstagramAccount
from app.models.base import utcnow
from app.models.enums import AuditAction, ContentStatus
from app.repositories import OAuthTokenRepository
from app.services.audit import AuditLogService
from app.services.instagram import InstagramAccountService

logger = logging.getLogger(__name__)

SYNC_ACTOR = SystemActor("analytics_sync")
INSIGHTS_SCOPE = "instagram_business_manage_insights"
ACCOUNT_WINDOWS = {"day": 1, "week": 7, "days_28": 28}

ClientFactory = Callable[[str, str], InstagramInsightsClient]


@dataclass(slots=True)
class AccountSyncResult:
    account_id: int
    username: str | None
    status: str  # "ok" | "skipped" | "failed"
    reason: str | None = None
    account_windows: int = 0
    media_synced: int = 0
    media_failed: int = 0
    unavailable: dict[str, list[str]] = field(default_factory=dict)


def engagement_rate(metrics: dict[str, Any]) -> float | None:
    reach, interactions = metrics.get("reach"), metrics.get("total_interactions")
    if isinstance(reach, int | float) and isinstance(interactions, int | float) and reach > 0:
        return round(float(interactions) / float(reach), 4)
    return None


class AnalyticsSyncService:
    def __init__(self, session: Session, client_factory: ClientFactory | None = None) -> None:
        self.session = session
        self.settings = get_settings()
        self.audit = AuditLogService(session)
        self.client_factory: ClientFactory = client_factory or (
            lambda token, ig: InstagramInsightsClient(token, ig, self.settings)
        )

    # ------------------------------------------------------------------ public
    def sync_all(self) -> list[AccountSyncResult]:
        accounts = self.session.scalars(
            select(InstagramAccount).where(InstagramAccount.deleted_at.is_(None))
        ).all()
        results = []
        for account in accounts:
            try:
                results.append(self.sync_account(account))
            except Exception:  # one broken account must not stop the others
                self.session.rollback()
                logger.exception("insights sync failed for account %s", account.id)
                results.append(
                    AccountSyncResult(account.id, account.username, "failed", "ichki xato")
                )
        return results

    def sync_account(self, account: InstagramAccount) -> AccountSyncResult:
        result = AccountSyncResult(account.id, account.username, "ok")
        token_row = OAuthTokenRepository(self.session).get_active_for_account(account.id)
        scopes = set(((token_row.scopes if token_row else None) or "").replace(",", " ").split())
        if token_row is not None and INSIGHTS_SCOPE not in scopes:
            return self._skip(
                result, f"{INSIGHTS_SCOPE} ruxsati berilmagan — akkauntni qayta ulang"
            )
        token = InstagramAccountService(self.session, self.audit).get_access_token(
            account.id, SYNC_ACTOR
        )
        if not token:
            return self._skip(result, "Token yo‘q yoki muddati o‘tgan — akkauntni qayta ulang")
        try:
            self._sync_account_windows(account, token, result)
        except MetaApiError as exc:
            return self._failed(result, exc)
        for content in self._recent_published(account):
            try:
                self._sync_media(account, token, content, result)
                result.media_synced += 1
            except MetaApiError as exc:
                result.media_failed += 1
                logger.warning(
                    "media_insights_failed",
                    extra={"content_id": content.id, "code": exc.code},
                )
        with atomic(self.session):
            self.audit.record(
                AuditAction.ANALYTICS_SYNCED,
                SYNC_ACTOR,
                details={
                    "instagram_account_id": account.id,
                    "account_windows": result.account_windows,
                    "media_synced": result.media_synced,
                    "media_failed": result.media_failed,
                    "unavailable": result.unavailable,
                },
            )
        return result

    # ------------------------------------------------------------------ account
    def _sync_account_windows(
        self, account: InstagramAccount, token: str, result: AccountSyncResult
    ) -> None:
        end = datetime.combine(utcnow().date(), time.min, tzinfo=UTC)
        counts = self._call(token, account.ig_user_id, lambda c: c.profile_counts())
        for period, days in ACCOUNT_WINDOWS.items():
            if self._has_window(account.id, period, end):
                continue
            start = end - timedelta(days=days)
            insights: InsightsResult = self._call(
                token, account.ig_user_id, lambda c, s=start: c.account_insights(s, end)
            )
            metrics: dict[str, Any] = dict(insights.metrics)
            if period == "day":  # point-in-time profile values, once per day
                for name in ("followers_count", "media_count"):
                    value = getattr(counts, name)
                    if value is not None:
                        metrics[name] = value
            with atomic(self.session):
                self.session.add(
                    AnalyticsSnapshot(
                        instagram_account_id=account.id,
                        scope="account",
                        period=period,
                        captured_at=utcnow(),
                        window_start=start,
                        window_end=end,
                        metrics=metrics,
                        unavailable=insights.unavailable,
                        api_version=self.settings.meta_graph_api_version,
                    )
                )
            result.account_windows += 1
            if insights.unavailable:
                result.unavailable[f"account:{period}"] = insights.unavailable

    def _has_window(self, account_id: int, period: str, end: datetime) -> bool:
        return (
            self.session.scalar(
                select(AnalyticsSnapshot.id).where(
                    AnalyticsSnapshot.instagram_account_id == account_id,
                    AnalyticsSnapshot.scope == "account",
                    AnalyticsSnapshot.period == period,
                    AnalyticsSnapshot.window_end == end,
                )
            )
            is not None
        )

    # ------------------------------------------------------------------ media
    def _recent_published(self, account: InstagramAccount) -> list[Content]:
        since = utcnow() - timedelta(days=self.settings.analytics_media_days)
        rows = self.session.scalars(
            select(Content).where(
                Content.status == ContentStatus.PUBLISHED,
                Content.ig_media_id.is_not(None),
                Content.published_at >= since,
                Content.deleted_at.is_(None),
            )
        ).all()
        # Content without an explicit account belongs to the only/connected account.
        return [c for c in rows if c.instagram_account_id in (None, account.id)]

    def _sync_media(
        self, account: InstagramAccount, token: str, content: Content, result: AccountSyncResult
    ) -> None:
        media_id = str(content.ig_media_id)
        details = self._call(token, account.ig_user_id, lambda c: c.media_details(media_id))
        insights: InsightsResult = self._call(
            token,
            account.ig_user_id,
            lambda c: c.media_insights(media_id, details.media_product_type),
        )
        metrics: dict[str, Any] = dict(insights.metrics)
        unavailable = list(insights.unavailable)
        # Plain media fields are also real Meta values; use them only where insights had none.
        for metric, value in (("likes", details.like_count), ("comments", details.comments_count)):
            if metric not in metrics and value is not None:
                metrics[metric] = value
                if metric in unavailable:
                    unavailable.remove(metric)
        rate = engagement_rate(metrics)
        now = utcnow()
        with atomic(self.session):
            self.session.add(
                AnalyticsSnapshot(
                    instagram_account_id=account.id,
                    content_id=content.id,
                    scope="media",
                    period="lifetime",
                    captured_at=now,
                    ig_media_id=media_id,
                    metrics=metrics,
                    unavailable=unavailable,
                    api_version=self.settings.meta_graph_api_version,
                )
            )
            perf = self.session.scalar(
                select(ContentPerformance).where(ContentPerformance.content_id == content.id)
            )
            if perf is None:
                perf = ContentPerformance(content_id=content.id)
                self.session.add(perf)
            perf.metrics = metrics
            perf.engagement_rate = rate
            perf.last_synced_at = now
        if unavailable:
            result.unavailable[f"media:{content.id}"] = unavailable

    # ------------------------------------------------------------------ helpers
    def _skip(self, result: AccountSyncResult, reason: str) -> AccountSyncResult:
        result.status, result.reason = "skipped", reason
        with atomic(self.session):
            self.audit.record(
                AuditAction.ANALYTICS_SYNC_FAILED,
                SYNC_ACTOR,
                status="SKIPPED",
                error=reason,
                details={"instagram_account_id": result.account_id},
            )
        return result

    def _failed(self, result: AccountSyncResult, exc: MetaApiError) -> AccountSyncResult:
        meta = (exc.details or {}).get("meta_message") if isinstance(exc.details, dict) else None
        result.status = "failed"
        result.reason = f"{exc.message} (Meta: {meta})" if meta else exc.message
        with atomic(self.session):
            self.audit.record(
                AuditAction.ANALYTICS_SYNC_FAILED,
                SYNC_ACTOR,
                status="FAILED",
                error=result.reason,
                details={"instagram_account_id": result.account_id, "code": exc.code},
            )
        return result

    def _call(
        self, token: str, ig_user_id: str, fn: Callable[[InstagramInsightsClient], Any]
    ) -> Any:
        async def go() -> Any:
            client = self.client_factory(token, ig_user_id)
            try:
                return await fn(client)
            finally:
                await client.aclose()

        return run_sync(go())
