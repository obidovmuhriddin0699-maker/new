"""Celery foundation. Run: celery -A app.workers.celery_app worker -l info

On Windows use the solo pool: ... worker -l info --pool=solo
"""

from celery import Celery
from celery.schedules import crontab

from app.core.config import get_settings

settings = get_settings()

celery_app = Celery(
    "muxriddin",
    broker=settings.effective_celery_broker_url,
    backend=settings.effective_celery_result_backend,
    include=[
        "app.workers.tasks.system",
        "app.workers.tasks.ai",
        "app.workers.tasks.instagram",
        "app.workers.tasks.publish",
        "app.workers.tasks.analytics",
    ],
)
celery_app.conf.update(
    task_always_eager=settings.celery_task_always_eager,
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    worker_prefetch_multiplier=1,
    broker_connection_retry_on_startup=True,
    # Celery beat (embedded in the dev worker with -B, or a separate `celery beat`).
    beat_schedule={
        "refresh-instagram-tokens": {
            "task": "instagram.refresh_tokens",
            "schedule": 6 * 60 * 60,  # every 6 hours; refresh only happens inside the window
        },
        "publish-due-schedules": {"task": "publish.process_due", "schedule": 60},
        "reconcile-publishing": {"task": "publish.reconcile", "schedule": 5 * 60},
        # Insights change slowly and Meta rate-limits calls: every 6 hours is plenty.
        "sync-insights": {"task": "analytics.sync", "schedule": 6 * 60 * 60},
        # Monday 03:10 UTC = 08:10 Asia/Tashkent, for the previous Monday–Sunday.
        "weekly-analytics-report": {
            "task": "analytics.weekly_report",
            "schedule": crontab(minute=10, hour=3, day_of_week=1),
        },
    },
)
