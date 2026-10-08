"""Tracks AI agent work. Jobs record provider/model/input/output for traceability."""

import time
from typing import Any

from sqlalchemy.orm import Session

from app.core.actors import Actor, AgentActor, SystemActor
from app.core.errors import ConflictError, NotFoundError, PermissionDeniedError
from app.core.transaction import atomic
from app.models import AIJob
from app.models.enums import AIJobStatus, AuditAction
from app.repositories import AIJobRepository
from app.services.audit import AuditLogService, sanitize


class AIJobService:
    def __init__(self, session: Session, audit: AuditLogService | None = None) -> None:
        self.session = session
        self.audit = audit or AuditLogService(session)
        self.repo = AIJobRepository(session)
        self._started: dict[int, float] = {}

    def create(
        self,
        actor: Actor,
        *,
        agent: str,
        input: dict[str, Any],
        content_id: int | None = None,
        provider: str | None = None,
        model: str | None = None,
    ) -> AIJob:
        self._require_runner(actor)
        with atomic(self.session):
            return self.repo.add(
                AIJob(
                    agent=agent,
                    content_id=content_id,
                    status=AIJobStatus.QUEUED,
                    provider=provider,
                    model=model,
                    input=sanitize(input),
                )
            )

    def start(self, job_id: int, actor: Actor) -> AIJob:
        self._require_runner(actor)
        with atomic(self.session):
            job = self._transition(job_id, {AIJobStatus.QUEUED}, AIJobStatus.RUNNING)
            self._started[job.id] = time.monotonic()
            self.audit.record(
                AuditAction.AI_JOB_STARTED,
                actor,
                content_id=job.content_id,
                details={"ai_job_id": job.id, "agent": job.agent, "model": job.model},
            )
            return job

    def succeed(self, job_id: int, actor: Actor, *, output: dict[str, Any]) -> AIJob:
        self._require_runner(actor)
        with atomic(self.session):
            job = self._transition(job_id, {AIJobStatus.RUNNING}, AIJobStatus.SUCCEEDED)
            job.output = sanitize(output)
            job.duration_ms = self._elapsed_ms(job.id)
            self.audit.record(
                AuditAction.AI_JOB_SUCCEEDED,
                actor,
                content_id=job.content_id,
                details={"ai_job_id": job.id, "duration_ms": job.duration_ms},
            )
            return job

    def fail(self, job_id: int, actor: Actor, *, error: str) -> AIJob:
        self._require_runner(actor)
        with atomic(self.session):
            job = self._transition(
                job_id, {AIJobStatus.QUEUED, AIJobStatus.RUNNING}, AIJobStatus.FAILED
            )
            job.error = error[:2000]
            job.duration_ms = self._elapsed_ms(job.id)
            self.audit.record(
                AuditAction.AI_JOB_FAILED,
                actor,
                content_id=job.content_id,
                status="FAILED",
                error=error,
                details={"ai_job_id": job.id},
            )
            return job

    def _transition(self, job_id: int, allowed: set[AIJobStatus], target: AIJobStatus) -> AIJob:
        job = self.repo.get_for_update(job_id)
        if job is None:
            raise NotFoundError("AI job not found")
        if job.status not in allowed:
            raise ConflictError(f"AI job is {job.status.value}, cannot become {target.value}")
        job.status = target
        return job

    def _elapsed_ms(self, job_id: int) -> int | None:
        started = self._started.pop(job_id, None)
        return int((time.monotonic() - started) * 1000) if started is not None else None

    @staticmethod
    def _require_runner(actor: Actor) -> None:
        if not isinstance(actor, AgentActor | SystemActor):
            raise PermissionDeniedError("AI jobs are run by agents or system workers")
