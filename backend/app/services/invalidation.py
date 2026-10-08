"""Helpers shared by content/approval/schedule services (no service imports here)."""

from collections.abc import Sequence

from sqlalchemy.orm import Session

from app.core.actors import Actor
from app.models import Approval, Content, ContentSchedule
from app.models.base import utcnow
from app.models.enums import AuditAction, ScheduleStatus
from app.repositories import ApprovalRepository, ContentScheduleRepository
from app.services.audit import AuditLogService


def invalidate_active_approvals(
    session: Session, audit: AuditLogService, content: Content, actor: Actor, reason: str
) -> Sequence[Approval]:
    approvals = ApprovalRepository(session).list_active_for_content(content.id)
    now = utcnow()
    for approval in approvals:
        approval.invalidated_at = now
        approval.invalidation_reason = reason
        audit.record(
            AuditAction.CONTENT_APPROVAL_INVALIDATED,
            actor,
            content_id=content.id,
            content_version=approval.content_version,
            details={"approval_id": approval.id, "reason": reason},
        )
    session.flush()
    return approvals


def cancel_pending_schedules(
    session: Session, audit: AuditLogService, content: Content, actor: Actor, reason: str
) -> Sequence[ContentSchedule]:
    schedules = ContentScheduleRepository(session).list_pending_for_content(content.id)
    for schedule in schedules:
        schedule.status = ScheduleStatus.CANCELLED
        schedule.last_error = reason
        # Free the idempotency key so the same version can be scheduled again later.
        schedule.idempotency_key = f"{schedule.idempotency_key}:cancelled:{schedule.id}"
        audit.record(
            AuditAction.CONTENT_SCHEDULE_CANCELLED,
            actor,
            content_id=content.id,
            content_version=schedule.content_version,
            details={"schedule_id": schedule.id, "reason": reason},
        )
    session.flush()
    return schedules
