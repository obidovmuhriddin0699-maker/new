"""Publishing tasks. Duplicate deliveries are harmless: a schedule must be claimed
(PENDING → PROCESSING) before anything is sent to Meta."""

from app.core.database import get_sessionmaker
from app.services.publish import PublishService
from app.workers.celery_app import celery_app


@celery_app.task(name="publish.execute")
def execute_publish(schedule_id: int) -> str:
    with get_sessionmaker()() as session:
        return PublishService(session).execute(schedule_id).status


@celery_app.task(name="publish.process_due")
def process_due_schedules() -> dict[str, int]:
    """Publish schedules whose time has come (skipped entirely when META_DRY_RUN=true)."""
    with get_sessionmaker()() as session:
        return PublishService(session).process_due()


@celery_app.task(name="publish.reconcile")
def reconcile_publishing() -> dict[str, int]:
    """Settle PROCESSING schedules left by a crash or a lost Meta response."""
    with get_sessionmaker()() as session:
        return PublishService(session).reconcile_stale()
