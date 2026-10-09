"""Analytics endpoints: stored Meta insights, manual sync, weekly analyst reports.

Every number comes from Meta (or is a documented ratio of two Meta numbers). Metrics
Meta did not return are listed as unavailable and shown as "—".
"""

from dataclasses import asdict
from datetime import date, datetime, timedelta
from typing import Annotated, Any

from fastapi import APIRouter, Query, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select

from app.api.deps import DbSession, HumanActorDep
from app.core.config import get_settings
from app.models import (
    AnalyticsSnapshot,
    AuditLog,
    Content,
    ContentPerformance,
    InstagramAccount,
)
from app.models.base import utcnow
from app.models.enums import AuditAction, ContentStatus
from app.schemas.errors import error_responses
from app.services.analytics_report import ENGAGEMENT_DEFINITION, AnalyticsReportService
from app.services.analytics_sync import AnalyticsSyncService
from app.services.guards import require_human_writer

router = APIRouter(prefix="/analytics", tags=["analytics"])


class WindowRead(BaseModel):
    period: str
    window_start: datetime | None
    window_end: datetime | None
    metrics: dict[str, Any]
    unavailable: list[str]
    captured_at: datetime


class ContentStatRead(BaseModel):
    content_id: int
    topic: str | None
    content_type: str
    published_at: datetime | None
    permalink: str | None
    metrics: dict[str, Any]
    unavailable: list[str]
    engagement_rate: float | None
    last_synced_at: datetime | None


class SyncStatusRead(BaseModel):
    at: datetime
    status: str
    message: str | None


class OverviewRead(BaseModel):
    account_id: int | None
    username: str | None
    windows: list[WindowRead]
    followers_count: int | None
    content: list[ContentStatRead]
    last_sync: SyncStatusRead | None
    engagement_rate_definition: str = ENGAGEMENT_DEFINITION
    note: str = "Only values returned by the Meta API. Missing metrics are never estimated."


class PointRead(BaseModel):
    date: date
    metrics: dict[str, Any]


class ReportRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    period_start: date
    period_end: date
    status: str
    summary: str
    highlights: list[dict[str, Any]]
    recommendations: list[str]
    facts: dict[str, Any]
    source: str
    provider: str | None
    model: str | None
    ai_rejected_reason: str | None
    created_by: str
    created_at: datetime


class ReportRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    week_start: date | None = Field(
        default=None, description="Monday of the week; default = last complete week"
    )


def _account(db) -> InstagramAccount | None:  # type: ignore[no-untyped-def]
    return db.scalars(
        select(InstagramAccount)
        .where(InstagramAccount.deleted_at.is_(None))
        .order_by(InstagramAccount.id)
        .limit(1)
    ).first()


@router.get(
    "/overview",
    response_model=OverviewRead,
    summary="Latest account windows (1/7/28 days) and per-content insights",
    responses=error_responses(401),
)
def overview(db: DbSession, _: HumanActorDep) -> OverviewRead:
    account = _account(db)
    windows: list[WindowRead] = []
    followers = None
    if account is not None:
        for period in ("day", "week", "days_28"):
            snap = db.scalars(
                select(AnalyticsSnapshot)
                .where(
                    AnalyticsSnapshot.instagram_account_id == account.id,
                    AnalyticsSnapshot.scope == "account",
                    AnalyticsSnapshot.period == period,
                )
                .order_by(AnalyticsSnapshot.window_end.desc(), AnalyticsSnapshot.id.desc())
                .limit(1)
            ).first()
            if snap is not None:
                windows.append(
                    WindowRead(
                        period=period,
                        window_start=snap.window_start,
                        window_end=snap.window_end,
                        metrics={k: v for k, v in snap.metrics.items() if k != "media_count"},
                        unavailable=snap.unavailable or [],
                        captured_at=snap.captured_at,
                    )
                )
                if period == "day":
                    value = snap.metrics.get("followers_count")
                    followers = value if isinstance(value, int) else None

    rows = db.execute(
        select(Content, ContentPerformance)
        .outerjoin(ContentPerformance, ContentPerformance.content_id == Content.id)
        .where(Content.status == ContentStatus.PUBLISHED, Content.deleted_at.is_(None))
        .order_by(Content.published_at.desc())
        .limit(50)
    ).all()
    content: list[ContentStatRead] = []
    for c, perf in rows:
        latest = db.scalars(
            select(AnalyticsSnapshot)
            .where(AnalyticsSnapshot.content_id == c.id, AnalyticsSnapshot.scope == "media")
            .order_by(AnalyticsSnapshot.id.desc())
            .limit(1)
        ).first()
        content.append(
            ContentStatRead(
                content_id=c.id,
                topic=c.topic,
                content_type=c.content_type.value,
                published_at=c.published_at,
                permalink=c.ig_permalink,
                metrics=perf.metrics if perf else {},
                unavailable=(latest.unavailable or []) if latest else [],
                engagement_rate=perf.engagement_rate if perf else None,
                last_synced_at=perf.last_synced_at if perf else None,
            )
        )

    last = db.scalars(
        select(AuditLog)
        .where(
            AuditLog.action.in_(
                [AuditAction.ANALYTICS_SYNCED.value, AuditAction.ANALYTICS_SYNC_FAILED.value]
            )
        )
        .order_by(AuditLog.id.desc())
        .limit(1)
    ).first()
    return OverviewRead(
        account_id=account.id if account else None,
        username=account.username if account else None,
        windows=windows,
        followers_count=followers,
        content=content,
        last_sync=SyncStatusRead(at=last.timestamp, status=last.status, message=last.error)
        if last
        else None,
    )


@router.get(
    "/history",
    response_model=list[PointRead],
    summary="Daily account values (1-day windows) for charts",
    responses=error_responses(401, 422),
)
def history(
    db: DbSession, _: HumanActorDep, days: Annotated[int, Query(ge=1, le=90)] = 30
) -> list[PointRead]:
    account = _account(db)
    if account is None:
        return []
    since = utcnow() - timedelta(days=days)
    snaps = db.scalars(
        select(AnalyticsSnapshot)
        .where(
            AnalyticsSnapshot.instagram_account_id == account.id,
            AnalyticsSnapshot.scope == "account",
            AnalyticsSnapshot.period == "day",
            AnalyticsSnapshot.window_end >= since,
        )
        .order_by(AnalyticsSnapshot.window_end)
    ).all()
    points: dict[date, dict[str, Any]] = {}
    for s in snaps:
        if s.window_start is not None:
            points[s.window_start.date()] = s.metrics
    return [PointRead(date=d, metrics=m) for d, m in points.items()]


@router.post(
    "/sync",
    summary="Pull insights from Meta now (read-only towards Instagram)",
    responses=error_responses(401, 403),
)
def sync_now(db: DbSession, actor: HumanActorDep) -> list[dict[str, Any]]:
    require_human_writer(db, actor)
    return [asdict(r) for r in AnalyticsSyncService(db).sync_all()]


@router.get(
    "/reports",
    response_model=list[ReportRead],
    summary="Weekly analyst reports (newest first)",
    responses=error_responses(401),
)
def reports(db: DbSession, _: HumanActorDep) -> list[ReportRead]:
    return [ReportRead.model_validate(r) for r in AnalyticsReportService(db).list()]


@router.get(
    "/reports/{report_id}",
    response_model=ReportRead,
    summary="One analyst report",
    responses=error_responses(401, 404),
)
def report(report_id: int, db: DbSession, _: HumanActorDep) -> ReportRead:
    return ReportRead.model_validate(AnalyticsReportService(db).get(report_id))


@router.post(
    "/reports",
    response_model=ReportRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create the weekly analyst report (AI phrasing, rule-based fallback)",
    description="Facts are computed from stored insights. With AI_JOBS_MODE=celery the "
    "report is queued (202) because a local model can take a while.",
    responses=error_responses(401, 403, 422) | {202: {"description": "Queued (celery mode)"}},
)
def create_report(
    body: ReportRequest, db: DbSession, actor: HumanActorDep
) -> ReportRead | JSONResponse:
    require_human_writer(db, actor)
    if get_settings().ai_jobs_mode == "celery":
        from app.workers.tasks.analytics import weekly_report_for

        weekly_report_for.delay(
            actor.user_id, body.week_start.isoformat() if body.week_start else None
        )
        return JSONResponse({"queued": True}, status_code=status.HTTP_202_ACCEPTED)
    created = AnalyticsReportService(db).create_weekly(actor, body.week_start)
    return ReportRead.model_validate(created)
