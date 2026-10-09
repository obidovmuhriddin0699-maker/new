"""Read models for the admin panel: overview counters and calendar.

Reach / engagement are shown only when real analytics rows exist (filled from the
Meta API by the insights sync). Otherwise they are ``None`` — never estimated.
"""

from dataclasses import dataclass, field
from datetime import UTC, date, datetime, time, timedelta
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.models import AnalyticsSnapshot, Content, ContentPerformance, ContentSchedule
from app.models.enums import ContentStatus, ScheduleStatus

MAX_CALENDAR_DAYS = 62


@dataclass(slots=True)
class DashboardSummary:
    total: int
    by_status: dict[str, int]
    pending_approval: int
    scheduled: int
    published: int
    failed: int
    drafts: int
    reach: int | None
    engagement_rate: float | None
    analytics_available: bool
    upcoming: list[dict[str, Any]] = field(default_factory=list)


@dataclass(slots=True)
class CalendarItem:
    content_id: int
    date: date
    at: datetime | None
    kind: str  # "scheduled" | "published" | "planned"
    content_type: str
    status: str
    topic: str | None
    version: int


class DashboardService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def summary(self) -> DashboardSummary:
        rows = self.session.execute(
            select(Content.status, func.count())
            .where(Content.deleted_at.is_(None))
            .group_by(Content.status)
        ).all()
        by_status = {s.value: 0 for s in ContentStatus}
        for status, count in rows:
            by_status[status.value if hasattr(status, "value") else status] = count

        reach = self._latest_account_metric("reach")
        engagement = self.session.scalar(
            select(func.avg(ContentPerformance.engagement_rate)).where(
                ContentPerformance.engagement_rate.is_not(None)
            )
        )
        upcoming = self.session.execute(
            select(ContentSchedule, Content)
            .join(Content, Content.id == ContentSchedule.content_id)
            .where(
                ContentSchedule.status == ScheduleStatus.PENDING,
                Content.deleted_at.is_(None),
            )
            .order_by(ContentSchedule.scheduled_at)
            .limit(5)
        ).all()
        return DashboardSummary(
            total=sum(by_status.values()),
            by_status=by_status,
            pending_approval=by_status[ContentStatus.READY_FOR_REVIEW.value],
            scheduled=by_status[ContentStatus.SCHEDULED.value],
            published=by_status[ContentStatus.PUBLISHED.value],
            failed=by_status[ContentStatus.FAILED.value],
            drafts=by_status[ContentStatus.DRAFT.value],
            reach=reach,
            engagement_rate=float(engagement) if engagement is not None else None,
            analytics_available=reach is not None or engagement is not None,
            upcoming=[
                {
                    "content_id": c.id,
                    "scheduled_at": s.scheduled_at,
                    "content_type": c.content_type.value,
                    "topic": c.topic,
                }
                for s, c in upcoming
            ],
        )

    def _latest_account_metric(self, name: str) -> int | None:
        snap = self.session.scalars(
            select(AnalyticsSnapshot)
            .where(AnalyticsSnapshot.scope == "account", AnalyticsSnapshot.period == "week")
            .order_by(AnalyticsSnapshot.captured_at.desc())
            .limit(1)
        ).first()
        if snap is None:
            return None
        value = (snap.metrics or {}).get(name)
        return int(value) if isinstance(value, int | float) else None

    def calendar(self, start: date, end: date) -> list[CalendarItem]:
        if end < start:
            raise AppError("end must not be before start", code="invalid_range")
        if (end - start).days + 1 > MAX_CALENDAR_DAYS:
            raise AppError(f"range is limited to {MAX_CALENDAR_DAYS} days", code="invalid_range")
        start_dt = datetime.combine(start, time.min, tzinfo=UTC)
        end_dt = datetime.combine(end + timedelta(days=1), time.min, tzinfo=UTC)
        items: list[CalendarItem] = []
        seen: set[int] = set()

        sched = self.session.execute(
            select(ContentSchedule, Content)
            .join(Content, Content.id == ContentSchedule.content_id)
            .where(
                Content.deleted_at.is_(None),
                ContentSchedule.status.in_(
                    [ScheduleStatus.PENDING, ScheduleStatus.PROCESSING, ScheduleStatus.DONE]
                ),
                ContentSchedule.scheduled_at >= start_dt,
                ContentSchedule.scheduled_at < end_dt,
            )
        ).all()
        for s, c in sched:
            items.append(self._item(c, s.scheduled_at.date(), s.scheduled_at, "scheduled"))
            seen.add(c.id)

        published = self.session.scalars(
            select(Content).where(
                Content.deleted_at.is_(None),
                Content.published_at >= start_dt,
                Content.published_at < end_dt,
            )
        ).all()
        for c in published:
            if c.id not in seen:
                items.append(self._item(c, c.published_at.date(), c.published_at, "published"))
                seen.add(c.id)

        planned = self.session.scalars(
            select(Content).where(
                Content.deleted_at.is_(None),
                Content.planned_date >= start,
                Content.planned_date <= end,
            )
        ).all()
        for c in planned:
            if c.id not in seen:
                items.append(self._item(c, c.planned_date, None, "planned"))
        items.sort(key=lambda i: (i.date, i.at or datetime.min.replace(tzinfo=UTC), i.content_id))
        return items

    @staticmethod
    def _item(c: Content, day: date, at: datetime | None, kind: str) -> CalendarItem:
        return CalendarItem(
            content_id=c.id,
            date=day,
            at=at,
            kind=kind,
            content_type=c.content_type.value,
            status=c.status.value,
            topic=c.topic,
            version=c.version,
        )
