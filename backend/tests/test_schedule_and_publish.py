from datetime import timedelta

import pytest

from app.core.errors import (
    AppError,
    ApprovalForbiddenError,
    ConflictError,
    InvalidStateTransitionError,
)
from app.models.base import utcnow
from app.models.enums import ContentStatus, ScheduleStatus
from app.repositories import AuditLogRepository
from app.services import (
    ApprovalService,
    ContentService,
    ScheduleService,
    publish_idempotency_key,
)
from tests.conftest import make_approved, make_ready


def test_schedule_requires_approval(db, human):
    content = make_ready(db, human)
    with pytest.raises(InvalidStateTransitionError):
        ScheduleService(db).schedule(content.id, human, scheduled_at=utcnow() + timedelta(hours=1))


def test_schedule_is_idempotent_and_bound_to_version(db, human):
    content = make_approved(db, human)
    service = ScheduleService(db)
    when = utcnow() + timedelta(hours=2)
    first = service.schedule(content.id, human, scheduled_at=when)
    second = service.schedule(content.id, human, scheduled_at=when + timedelta(hours=1))
    assert first.created and not second.created
    assert first.schedule.id == second.schedule.id
    assert first.schedule.idempotency_key == publish_idempotency_key(content.id, 1)
    assert first.schedule.content_version == 1
    assert first.schedule.approval_id is not None
    assert content.status == ContentStatus.SCHEDULED


def test_schedule_validation(db, human, agent):
    content = make_approved(db, human)
    service = ScheduleService(db)
    with pytest.raises(AppError):
        service.schedule(content.id, human, scheduled_at=utcnow() - timedelta(days=1))
    with pytest.raises(AppError):
        service.schedule(content.id, human, scheduled_at=utcnow().replace(tzinfo=None))
    with pytest.raises(ApprovalForbiddenError):
        service.schedule(content.id, agent, scheduled_at=utcnow() + timedelta(hours=1))


def test_edit_cancels_schedule_and_requires_new_approval(db, human):
    content = make_approved(db, human)
    sched = ScheduleService(db).schedule(content.id, human, scheduled_at=utcnow() + timedelta(1))
    ContentService(db).update(content.id, human, expected_version=1, changes={"caption": "new"})
    db.refresh(sched.schedule)
    assert sched.schedule.status == ScheduleStatus.CANCELLED
    assert content.status == ContentStatus.READY_FOR_REVIEW
    ApprovalService(db).approve(content.id, human, expected_version=2)
    again = ScheduleService(db).schedule(content.id, human, scheduled_at=utcnow() + timedelta(1))
    assert again.created and again.schedule.content_version == 2


def test_unschedule_and_reschedule_same_version(db, human):
    content = make_approved(db, human)
    service = ScheduleService(db)
    service.schedule(content.id, human, scheduled_at=utcnow() + timedelta(hours=1))
    service.unschedule(content.id, human)
    assert content.status == ContentStatus.APPROVED
    again = service.schedule(content.id, human, scheduled_at=utcnow() + timedelta(hours=3))
    assert again.created


def test_due_schedules(db, human):
    content = make_approved(db, human)
    service = ScheduleService(db)
    service.schedule(content.id, human, scheduled_at=utcnow())
    assert [s.content_id for s in service.due(utcnow() + timedelta(seconds=1))] == [content.id]
    assert service.due(utcnow() - timedelta(hours=1)) == []


def test_publish_state_flow_without_instagram(db, human, publisher):
    content = make_approved(db, human)
    service = ContentService(db)
    approval = service.start_publishing(content.id, publisher)
    assert content.status == ContentStatus.PUBLISHING
    assert approval.content_version == 1
    service.mark_published(content.id, publisher, ig_media_id="mock-media-1")
    assert content.status == ContentStatus.PUBLISHED
    actions = [e.action for e in AuditLogRepository(db).list_for_content(content.id)]
    assert "CONTENT_PUBLISH_STARTED" in actions and "CONTENT_PUBLISH_SUCCEEDED" in actions
    started = next(
        e
        for e in AuditLogRepository(db).list_for_content(content.id)
        if e.action == "CONTENT_PUBLISH_STARTED"
    )
    assert started.details["approved_by_user_id"] == human.user_id


def test_scheduled_publish_marks_schedule_done_and_blocks_duplicates(db, human, publisher):
    content = make_approved(db, human)
    ScheduleService(db).schedule(content.id, human, scheduled_at=utcnow())
    service = ContentService(db)
    service.start_publishing(content.id, publisher)
    service.mark_published(content.id, publisher, ig_media_id="m-2")
    assert content.schedules[0].status == ScheduleStatus.DONE
    with pytest.raises(InvalidStateTransitionError):
        service.start_publishing(content.id, publisher)


def test_failed_publish_retry_still_needs_valid_approval(db, human, publisher):
    content = make_approved(db, human)
    service = ContentService(db)
    service.start_publishing(content.id, publisher)
    service.mark_publish_failed(content.id, publisher, error="Rate limit")
    assert content.status == ContentStatus.FAILED
    service.start_publishing(content.id, publisher)  # same approved version: allowed
    service.mark_publish_failed(content.id, publisher, error="again")
    service.update(content.id, human, expected_version=1, changes={"caption": "fix"})
    assert content.status == ContentStatus.READY_FOR_REVIEW
    with pytest.raises(InvalidStateTransitionError):
        service.start_publishing(content.id, publisher)


def test_already_published_version_cannot_restart(db, human, publisher):
    content = make_approved(db, human)
    ScheduleService(db).schedule(content.id, human, scheduled_at=utcnow())
    service = ContentService(db)
    service.start_publishing(content.id, publisher)
    service.mark_publish_failed(content.id, publisher, error="timeout after publish?")
    # Simulate the worker having recorded success on the schedule before the failure.
    content.schedules[0].status = ScheduleStatus.DONE
    db.commit()
    with pytest.raises(ConflictError):
        service.start_publishing(content.id, publisher)
