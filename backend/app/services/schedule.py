"""Scheduling of approved content (idempotent). No publishing happens here."""

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime, timedelta

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.actors import Actor, HumanActor
from app.core.errors import AppError, ConflictError, NotFoundError
from app.core.transaction import atomic
from app.models import ContentSchedule
from app.models.base import utcnow
from app.models.enums import AuditAction, ContentStatus, ScheduleStatus
from app.repositories import ContentRepository, ContentScheduleRepository
from app.services.approval import ApprovalService
from app.services.audit import AuditLogService
from app.services.content_state import apply_transition, assert_transition
from app.services.guards import require_human_approver
from app.services.invalidation import cancel_pending_schedules

# Allow small clock skew for "publish now" style schedules.
_PAST_TOLERANCE = timedelta(minutes=1)


def publish_idempotency_key(content_id: int, version: int) -> str:
    """One publish per content version — reused by the PHASE 8 publish worker."""
    return f"publish:content:{content_id}:v{version}"


@dataclass(frozen=True, slots=True)
class ScheduleResult:
    schedule: ContentSchedule
    created: bool


class ScheduleService:
    def __init__(self, session: Session, audit: AuditLogService | None = None) -> None:
        self.session = session
        self.audit = audit or AuditLogService(session)
        self.contents = ContentRepository(session)
        self.schedules = ContentScheduleRepository(session)
        self.approvals = ApprovalService(session, self.audit)

    def schedule(self, content_id: int, actor: Actor, *, scheduled_at: datetime) -> ScheduleResult:
        """Schedule the current approved version. Scheduling is a human decision."""
        key: str | None = None
        try:
            with atomic(self.session):
                require_human_approver(self.session, actor)
                content = self.contents.get_for_update(content_id)
                if content is None:
                    raise NotFoundError("Content not found")
                key = publish_idempotency_key(content.id, content.version)
                existing = self.schedules.get_by_idempotency_key(key)
                if existing is not None:
                    return ScheduleResult(existing, created=False)

                if scheduled_at.tzinfo is None:
                    raise AppError("scheduled_at must include a timezone", code="invalid_datetime")
                if scheduled_at < utcnow() - _PAST_TOLERANCE:
                    raise AppError("scheduled_at is in the past", code="invalid_datetime")

                assert_transition(content.status, ContentStatus.SCHEDULED)
                approval = self.approvals.require_valid_approval(content)
                schedule = self.schedules.add(
                    ContentSchedule(
                        content_id=content.id,
                        content_version=content.version,
                        approval_id=approval.id,
                        created_by_user_id=actor.user_id if isinstance(actor, HumanActor) else None,
                        scheduled_at=scheduled_at,
                        status=ScheduleStatus.PENDING,
                        idempotency_key=key,
                    )
                )
                apply_transition(content, ContentStatus.SCHEDULED)
                self.audit.record(
                    AuditAction.CONTENT_SCHEDULED,
                    actor,
                    content_id=content.id,
                    content_version=content.version,
                    details={
                        "schedule_id": schedule.id,
                        "scheduled_at": scheduled_at.isoformat(),
                        "approval_id": approval.id,
                        "idempotency_key": key,
                    },
                )
                return ScheduleResult(schedule, created=True)
        except IntegrityError:
            if key is None:
                raise
            existing = self.schedules.get_by_idempotency_key(key)
            if existing is None:
                raise
            return ScheduleResult(existing, created=False)

    def unschedule(self, content_id: int, actor: Actor) -> None:
        with atomic(self.session):
            require_human_approver(self.session, actor)
            content = self.contents.get_for_update(content_id)
            if content is None:
                raise NotFoundError("Content not found")
            if content.status != ContentStatus.SCHEDULED:
                raise ConflictError("Content is not scheduled")
            cancel_pending_schedules(self.session, self.audit, content, actor, "unscheduled")
            apply_transition(content, ContentStatus.APPROVED)

    def due(self, now: datetime | None = None, limit: int = 20) -> Sequence[ContentSchedule]:
        """Pending schedules whose time has come (consumed by the PHASE 8 worker)."""
        return self.schedules.list_due(now or utcnow(), limit=limit)
