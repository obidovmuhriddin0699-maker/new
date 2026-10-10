"""Background execution of AI jobs (used when AI_JOBS_MODE=celery)."""

from app.core.database import get_sessionmaker
from app.services.ai_content import AIContentService
from app.workers.celery_app import celery_app


@celery_app.task(name="ai.run_job", acks_late=True, max_retries=0)
def run_ai_job(job_id: int) -> str:
    """Execute one AI job. Idempotent: a job that is no longer QUEUED is not re-run."""
    with get_sessionmaker()() as session:
        outcome = AIContentService(session).execute(job_id)
        return outcome.job.status.value
