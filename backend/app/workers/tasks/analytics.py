"""Analytics tasks: insights sync (read-only towards Meta) and the weekly analyst report."""

from dataclasses import asdict

from app.core.database import get_sessionmaker
from app.workers.celery_app import celery_app


@celery_app.task(name="analytics.sync")
def sync_insights() -> list[dict]:
    from app.services.analytics_sync import AnalyticsSyncService

    with get_sessionmaker()() as session:
        return [asdict(r) for r in AnalyticsSyncService(session).sync_all()]


@celery_app.task(name="analytics.weekly_report")
def weekly_report() -> int | None:
    """Report for the last complete Monday–Sunday week, then notify Telegram approvers."""
    from app.services.analytics_report import ANALYST_ACTOR, AnalyticsReportService

    with get_sessionmaker()() as session:
        report = AnalyticsReportService(session).create_weekly(ANALYST_ACTOR)
        return report.id


@celery_app.task(name="analytics.weekly_report_for")
def weekly_report_for(user_id: int, week_start: str | None) -> int:
    """Report requested from the panel (queued in AI_JOBS_MODE=celery)."""
    from datetime import date

    from app.core.actors import HumanActor
    from app.services.analytics_report import AnalyticsReportService

    with get_sessionmaker()() as session:
        report = AnalyticsReportService(session).create_weekly(
            HumanActor(user_id=user_id), date.fromisoformat(week_start) if week_start else None
        )
        return report.id
