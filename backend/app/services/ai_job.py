"""Tracks AI work: type, status, timing, safe error info, related content.

Job records hold the validated request parameters and validated output only —
never prompts, provider credentials or tokens (inputs are also redacted).
"""

from collections.abc import Sequence
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.actors import Actor, AgentActor, SystemActor
from app.core.errors import ConflictError, NotFoundError, PermissionDeniedError
from app.core.transaction import atomic
from app.models import AIJob
from app.models.base import utcnow
from app.models.enums import AIJobStatus, AuditAction
from app.repositories import AIJobRepository
from app.services.audit import AuditLogService, sanitize

ACTIVE_STATUSES = (AIJobStatus.QUEUED, AIJobStatus.RUNNING)


class AIJobService:
    def __init__(self, session: Session, audit: AuditLogService | None = None) -> None:
        self.session = session
        self.audit = audit or AuditLogService(session)
        self.repo = AIJobRepository(session)

    def get(self, job_id: int) -> AIJob:
        job = self.repo.get(job_id)
        if job is None:
            raise NotFoundError("AI job not found")
        return job

    def list_recent(self, *, user_id: int | None = None, limit: int = 20) -> Sequence[AIJob]:
        stmt = select(AIJob).order_by(AIJob.id.desc()).limit(limit)
        if user_id is not None:
            stmt = stmt.where(AIJob.created_by_user_id == user_id)
        return self.session.scalars(stmt).all()

    def count_active_for_user(self, user_id: int) -> int:
        return (
            self.session.scalar(
                select(func.count()).where(
                    AIJob.created_by_user_id == user_id, AIJob.status.in_(ACTIVE_STATUSES)
                )
            )
            or 0
        )

    def create(
        self,
        actor: Actor,
        *,
        agent: str,
        input: dict[str, Any],
        job_type: str = "generic",
        content_id: int | None = None,
        provider: str | None = None,
        model: str | None = None,
        created_by_user_id: int | None = None,
    ) -> AIJob:
        self._require_runner(actor)
        with atomic(self.session):
            return self.repo.add(
                AIJob(
                    agent=agent,
                    job_type=job_type,
                    content_id=content_id,
                    status=AIJobStatus.QUEUED,
                    provider=provider,
                    model=model,
                    input=sanitize(input),
                    created_by_user_id=created_by_user_id,
                )
            )

    def start(self, job_id: int, actor: Actor) -> AIJob:
        self._require_runner(actor)
        with atomic(self.session):
            job = self._transition(job_id, {AIJobStatus.QUEUED}, AIJobStatus.RUNNING)
            job.started_at = utcnow()
            self.audit.record(
                AuditAction.AI_JOB_STARTED,
                actor,
                content_id=job.content_id,
                details={"ai_job_id": job.id, "job_type": job.job_type, "model": job.model},
            )
            return job

    def succeed(
        self, job_id: int, actor: Actor, *, output: dict[str, Any], content_id: int | None = None
    ) -> AIJob:
        self._require_runner(actor)
        with atomic(self.session):
            job = self._transition(job_id, {AIJobStatus.RUNNING}, AIJobStatus.SUCCEEDED)
            job.output = sanitize(output)
            if content_id is not None:
                job.content_id = content_id
            self._finish(job)
            self.audit.record(
                AuditAction.AI_JOB_SUCCEEDED,
                actor,
                content_id=job.content_id,
                details={
                    "ai_job_id": job.id,
                    "job_type": job.job_type,
                    "duration_ms": job.duration_ms,
                },
            )
            return job

    def fail(self, job_id: int, actor: Actor, *, error: str, category: str = "internal") -> AIJob:
        self._require_runner(actor)
        with atomic(self.session):
            job = self._transition(
                job_id, {AIJobStatus.QUEUED, AIJobStatus.RUNNING}, AIJobStatus.FAILED
            )
            job.error = error[:1000]
            job.error_category = category[:50]
            self._finish(job)
            self.audit.record(
                AuditAction.AI_JOB_FAILED,
                actor,
                content_id=job.content_id,
                status="FAILED",
                error=job.error,
                details={"ai_job_id": job.id, "job_type": job.job_type, "category": category},
            )
            return job

    @staticmethod
    def _finish(job: AIJob) -> None:
        job.finished_at = utcnow()
        if job.started_at is not None:
            job.duration_ms = int((job.finished_at - job.started_at).total_seconds() * 1000)

    def _transition(self, job_id: int, allowed: set[AIJobStatus], target: AIJobStatus) -> AIJob:
        job = self.repo.get_for_update(job_id)
        if job is None:
            raise NotFoundError("AI job not found")
        if job.status not in allowed:
            raise ConflictError(f"AI job is {job.status.value}, cannot become {target.value}")
        job.status = target
        return job

    @staticmethod
    def _require_runner(actor: Actor) -> None:
        if not isinstance(actor, AgentActor | SystemActor):
            raise PermissionDeniedError("AI jobs are run by agents or system workers")
