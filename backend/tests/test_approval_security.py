"""Critical approval/publish rules (PHASE 2 acceptance criteria)."""

from datetime import timedelta

import pytest
from sqlalchemy import select, update

from app.core.actors import AgentActor, HumanActor, SystemActor
from app.core.errors import (
    ApprovalForbiddenError,
    ApprovalRequiredError,
    InvalidStateTransitionError,
    PermissionDeniedError,
    VersionMismatchError,
)
from app.models import Approval, AuditLog, Content
from app.models.base import utcnow
from app.models.enums import ApprovalChannel, ApprovalDecision, ContentStatus
from app.repositories import ApprovalRepository
from app.services import ApprovalService, ContentService, ScheduleService
from tests.conftest import make_approved, make_content, make_ready


# 1. DRAFT cannot become PUBLISHED --------------------------------------------------------
def test_draft_cannot_become_published(db, human, publisher):
    content = make_content(db, human)
    service = ContentService(db)
    with pytest.raises(InvalidStateTransitionError):
        service.mark_published(content.id, publisher, ig_media_id="x")
    with pytest.raises(InvalidStateTransitionError):
        service.start_publishing(content.id, publisher)
    db.refresh(content)
    assert content.status == ContentStatus.DRAFT


# 2. READY_FOR_REVIEW cannot become PUBLISHING without human approval ---------------------
def test_ready_for_review_cannot_start_publishing(db, human, publisher):
    content = make_ready(db, human)
    with pytest.raises(InvalidStateTransitionError):
        ContentService(db).start_publishing(content.id, publisher)
    db.refresh(content)
    assert content.status == ContentStatus.READY_FOR_REVIEW


def test_forced_approved_status_without_approval_record_cannot_publish(db, human, publisher):
    """Even if status were tampered to APPROVED, no approval row => no publishing."""
    content = make_ready(db, human)
    db.execute(update(Content).where(Content.id == content.id).values(status="APPROVED"))
    db.commit()
    db.refresh(content)
    with pytest.raises(ApprovalRequiredError):
        ContentService(db).start_publishing(content.id, publisher)
    db.refresh(content)
    assert content.status == ContentStatus.APPROVED


# 3. Approved version 1 cannot authorize modified version 2 -------------------------------
def test_approval_of_v1_does_not_authorize_v2(db, human, publisher):
    content = make_approved(db, human)
    service = ContentService(db)
    assert service.is_publish_authorized(content)
    service.update(content.id, human, expected_version=1, changes={"caption": "v2 matni"})
    assert content.version == 2
    assert content.status == ContentStatus.READY_FOR_REVIEW
    assert not service.is_publish_authorized(content)
    with pytest.raises(InvalidStateTransitionError):
        service.start_publishing(content.id, publisher)


def test_v1_approval_row_cannot_be_reused_even_if_status_forced(db, human, publisher):
    content = make_approved(db, human)
    ContentService(db).update(content.id, human, expected_version=1, changes={"caption": "v2"})
    db.execute(update(Content).where(Content.id == content.id).values(status="APPROVED"))
    db.commit()
    db.refresh(content)
    with pytest.raises(ApprovalRequiredError):
        ContentService(db).start_publishing(content.id, publisher)


def test_tampered_content_without_new_version_is_not_authorized(db, human, publisher):
    """A direct DB edit that bypasses versioning breaks the hash -> not publishable."""
    content = make_approved(db, human)
    db.execute(update(Content).where(Content.id == content.id).values(caption="tampered"))
    db.commit()
    db.refresh(content)
    assert not ContentService(db).is_publish_authorized(content)
    with pytest.raises(ApprovalRequiredError):
        ContentService(db).start_publishing(content.id, publisher)


def test_approve_requires_reviewed_version(db, human):
    content = make_ready(db, human)
    ContentService(db).update(content.id, human, expected_version=1, changes={"caption": "new"})
    with pytest.raises(VersionMismatchError):
        ApprovalService(db).approve(content.id, human, expected_version=1)
    assert ApprovalService(db).approve(content.id, human, expected_version=2).created


# 4. AI/service cannot impersonate human approval -----------------------------------------
@pytest.mark.parametrize(
    "actor",
    [
        AgentActor(name="content_creator"),
        SystemActor("publish_service"),
        SystemActor("scheduler"),
    ],
)
def test_non_human_actors_cannot_approve(db, human, actor):
    content = make_ready(db, human)
    for call in (
        ApprovalService(db).approve,
        ApprovalService(db).reject,
        ApprovalService(db).request_edit,
    ):
        with pytest.raises(ApprovalForbiddenError):
            call(content.id, actor, expected_version=1)
    assert ApprovalRepository(db).list_for_content(content.id) == []
    db.refresh(content)
    assert content.status == ContentStatus.READY_FOR_REVIEW


def test_forged_human_actor_is_rejected(db, human):
    content = make_ready(db, human)
    with pytest.raises(ApprovalForbiddenError):
        ApprovalService(db).approve(content.id, HumanActor(user_id=99999), expected_version=1)
    denied = db.scalars(select(AuditLog).where(AuditLog.action == "APPROVAL_DENIED")).one()
    assert denied.actor_user_id is None
    assert denied.details["claimed_user_id"] == 99999


def test_inactive_or_viewer_cannot_approve(db, human, viewer, user):
    content = make_ready(db, human)
    with pytest.raises(ApprovalForbiddenError):
        ApprovalService(db).approve(content.id, viewer, expected_version=1)
    user.is_active = False
    db.commit()
    with pytest.raises(ApprovalForbiddenError):
        ApprovalService(db).approve(content.id, human, expected_version=1)


def test_denied_approval_is_audited(db, human):
    content = make_ready(db, human)
    with pytest.raises(ApprovalForbiddenError):
        ApprovalService(db).approve(content.id, AgentActor(name="rogue"), expected_version=1)
    denied = db.scalars(select(AuditLog).where(AuditLog.action == "APPROVAL_DENIED")).all()
    assert len(denied) == 1
    assert denied[0].actor_type.value == "AGENT"
    assert denied[0].content_id == content.id
    assert denied[0].status == "DENIED"


def test_approval_revoked_when_approver_deactivated(db, human, user):
    content = make_approved(db, human)
    assert ContentService(db).is_publish_authorized(content)
    user.is_active = False
    db.commit()
    assert not ContentService(db).is_publish_authorized(content)


def test_agent_cannot_start_publishing(db, human, agent):
    content = make_approved(db, human)
    with pytest.raises(PermissionDeniedError):
        ContentService(db).start_publishing(content.id, agent)
    with pytest.raises(PermissionDeniedError):
        ContentService(db).start_publishing(content.id, human)  # humans approve, service publishes
    db.refresh(content)
    assert content.status == ContentStatus.APPROVED


# 5. Rejected content cannot publish ------------------------------------------------------
def test_rejected_content_cannot_publish(db, human, publisher):
    content = make_ready(db, human)
    ApprovalService(db).reject(content.id, human, expected_version=1, comment="Yo‘q")
    assert content.status == ContentStatus.REJECTED
    service = ContentService(db)
    with pytest.raises(InvalidStateTransitionError):
        service.start_publishing(content.id, publisher)
    with pytest.raises(ApprovalForbiddenError):
        ApprovalService(db).approve(content.id, AgentActor(name="x"), expected_version=1)
    with pytest.raises(InvalidStateTransitionError):
        ApprovalService(db).approve(content.id, human, expected_version=1)
    with pytest.raises(InvalidStateTransitionError):
        service.update(content.id, human, expected_version=1, changes={"caption": "again"})


# 6. Editing approved content invalidates previous approval -------------------------------
def test_edit_invalidates_previous_approval(db, human):
    content = make_approved(db, human)
    approval = ApprovalRepository(db).get_active_approval(content.id, 1)
    assert approval is not None
    ContentService(db).update(content.id, human, expected_version=1, changes={"cta": "Yangi CTA"})
    db.refresh(approval)
    assert approval.invalidated_at is not None
    assert "content changed" in approval.invalidation_reason
    assert ApprovalRepository(db).list_active_for_content(content.id) == []
    # The new version needs (and can get) its own approval.
    result = ApprovalService(db).approve(content.id, human, expected_version=2)
    assert result.created and result.approval.content_version == 2
    assert ContentService(db).is_publish_authorized(content)


def test_request_edit_after_approval_invalidates_and_cancels_schedule(db, human):
    content = make_approved(db, human)
    ScheduleService(db).schedule(content.id, human, scheduled_at=utcnow() + timedelta(days=1))
    ApprovalService(db).request_edit(
        content.id, human, expected_version=1, comment="Rangini o‘zgartir"
    )
    assert content.status == ContentStatus.EDIT_REQUESTED
    assert ApprovalRepository(db).list_active_for_content(content.id) == []
    assert content.schedules[0].status.value == "CANCELLED"


# Idempotency & concurrency ---------------------------------------------------------------
def test_approve_is_idempotent(db, human):
    content = make_ready(db, human)
    first = ApprovalService(db).approve(content.id, human, expected_version=1)
    second = ApprovalService(db).approve(content.id, human, expected_version=1)
    assert first.created and not second.created
    assert first.approval.id == second.approval.id
    assert len(ApprovalRepository(db).list_for_content(content.id)) == 1


def test_db_enforces_single_active_approval_per_version(db, human, user):
    content = make_approved(db, human)
    approval = ApprovalRepository(db).get_active_approval(content.id, 1)
    db.add(
        Approval(
            content_id=content.id,
            content_version=1,
            content_hash=approval.content_hash,
            decision=ApprovalDecision.APPROVED,
            decided_by_user_id=user.id,
            channel=ApprovalChannel.WEB,
        )
    )
    from sqlalchemy.exc import IntegrityError

    with pytest.raises(IntegrityError):
        db.commit()
    db.rollback()


def test_approval_records_who_and_what(db, human, user):
    content = make_approved(db, human)
    approval = ApprovalRepository(db).get_active_approval(content.id, 1)
    assert approval.decided_by_user_id == user.id
    assert approval.content_version == 1
    assert approval.channel == ApprovalChannel.WEB
    assert len(approval.content_hash) == 64
    assert approval.created_at is not None
    event = db.scalars(select(AuditLog).where(AuditLog.action == "CONTENT_APPROVED")).one()
    assert event.actor_user_id == user.id and event.content_version == 1
    assert event.details["approval_id"] == approval.id


def test_no_approved_flag_shortcut_on_content():
    columns = set(Content.__table__.columns.keys())
    assert not {"approved", "is_approved", "approved_by", "approved_version"} & columns
