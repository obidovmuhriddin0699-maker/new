"""PHASE 8: Instagram publishing. Meta is a stateful fake behind respx — nothing real."""

import logging
from datetime import timedelta

import pytest
import respx
from sqlalchemy import delete, select, update

from app.core.actors import AgentActor
from app.core.config import get_settings
from app.core.errors import (
    ApprovalForbiddenError,
    ApprovalRequiredError,
    ConflictError,
    PermissionDeniedError,
)
from app.integrations.meta.errors import MetaErrorKind, classify
from app.models import AuditLog, ContentSchedule, InstagramAccount
from app.models.base import utcnow
from app.models.enums import (
    AuditAction,
    ContentStatus,
    ContentType,
    InstagramAccountType,
    ScheduleStatus,
)
from app.services import ApprovalService, ContentService, ScheduleService
from app.services.publish import PublishService, build_plan
from app.services.review import ReviewService
from tests.conftest import IG_PUBLISH_ID, PUBLISH_TOKEN, make_publishable, make_ready
from tests.meta_publish_fake import FakeMeta

pytestmark = pytest.mark.usefixtures("publish_settings")


@pytest.fixture
def meta():
    fake = FakeMeta(ig_user_id=IG_PUBLISH_ID)
    with respx.mock(assert_all_called=False) as router:
        router.route(host="graph.instagram.com").mock(side_effect=fake.handler)
        yield fake


@pytest.fixture
def api(client, auth_headers):
    client.headers.update(auth_headers)
    return client


def service(db, sleeps=None):
    return PublishService(db, sleep=(sleeps.append if sleeps is not None else lambda _s: None))


def actions(db, content_id=None):
    stmt = select(AuditLog).order_by(AuditLog.id)
    if content_id is not None:
        stmt = stmt.where(AuditLog.content_id == content_id)
    return [a.action for a in db.scalars(stmt)]


def publish(db, human, content):
    return service(db).request_publish(content.id, human, expected_version=content.version)


# ================================================================== plan
def test_plan_post_uses_approved_snapshot_and_full_caption(db, human):
    content = make_publishable(db, human)
    version = ContentService(db).versions.get_version(content.id, content.version)
    plan = build_plan(version)
    assert plan.items == [{"image_url": "https://cdn.example/a.jpg", "caption": plan.caption}]
    assert plan.caption.startswith("Kichik xona katta ko‘rinadi\n\nMinimalizm haqida post")
    assert plan.caption.endswith("Saqlab qo‘ying\n\n#interior")
    assert plan.final is None
    assert [s.endpoint for s in plan.steps()][-1] == "POST /{ig-user-id}/media_publish"


@pytest.mark.parametrize(
    ("ct", "expected"),
    [
        (ContentType.REELS, {"media_type": "REELS", "share_to_feed": "true"}),
        (ContentType.STORY, {"media_type": "STORIES", "image_url": "https://cdn.example/s.jpg"}),
    ],
)
def test_plan_reels_and_story(db, human, ct, expected):
    content = make_publishable(db, human, content_type=ct)
    plan = build_plan(ContentService(db).versions.get_version(content.id, content.version))
    assert expected.items() <= plan.items[0].items()
    if ct == ContentType.STORY:
        assert "caption" not in plan.items[0] and plan.caption == ""


def test_plan_carousel(db, human):
    content = make_publishable(db, human, content_type=ContentType.CAROUSEL)
    plan = build_plan(ContentService(db).versions.get_version(content.id, content.version))
    assert [i["is_carousel_item"] for i in plan.items] == ["true", "true"]
    assert [i["image_url"] for i in plan.items] == [
        "https://cdn.example/1.jpg",
        "https://cdn.example/2.jpg",
    ]
    assert plan.final == {"media_type": "CAROUSEL", "caption": plan.caption}


# ================================================================== dry run
def test_dry_run_sends_nothing_and_changes_nothing(db, human, ig_account, meta, monkeypatch):
    monkeypatch.setattr(get_settings(), "meta_dry_run", True)
    content = make_publishable(db, human)
    result = publish(db, human, content)
    assert result.status == "dry_run" and result.preview is not None
    assert result.preview.plan and result.preview.plan.items
    assert meta.requests == []
    db.expire_all()
    assert ContentService(db).get(content.id).status == ContentStatus.APPROVED
    assert db.scalars(select(ContentSchedule)).first() is None
    assert AuditAction.CONTENT_PUBLISH_DRY_RUN.value in actions(db, content.id)
    assert PublishService(db).process_due()["processed"] == 0


# ================================================================== happy paths
def test_publish_post_end_to_end(db, human, user, ig_account, meta):
    content = make_publishable(db, human)
    result = publish(db, human, content)
    assert result.status == "published", result.message
    db.expire_all()
    c = ContentService(db).get(content.id)
    assert c.status == ContentStatus.PUBLISHED and c.ig_media_id in meta.media
    assert c.ig_permalink == meta.media[c.ig_media_id]["permalink"]
    schedule = db.scalars(select(ContentSchedule)).one()
    assert schedule.status == ScheduleStatus.DONE and schedule.ig_media_id == c.ig_media_id
    assert meta.publish_calls == 1 and len(meta.containers) == 1
    # caption sent = the approved snapshot's published caption
    sent = next(iter(meta.containers.values())).params
    assert (
        sent["caption"].endswith("#interior") and sent["image_url"] == "https://cdn.example/a.jpg"
    )
    acts = actions(db, content.id)
    for a in (
        AuditAction.CONTENT_PUBLISH_REQUESTED,
        AuditAction.CONTENT_PUBLISH_STARTED,
        AuditAction.INSTAGRAM_CONTAINER_CREATED,
        AuditAction.CONTENT_PUBLISH_SUCCEEDED,
    ):
        assert a.value in acts
    done = db.scalars(
        select(AuditLog).where(AuditLog.action == AuditAction.CONTENT_PUBLISH_SUCCEEDED.value)
    ).one()
    assert done.details["approved_by_user_id"] == user.id
    assert done.details["requested_by_user_id"] == user.id
    assert done.details["ig_media_id"] == c.ig_media_id


def test_carousel_creates_children_then_parent(db, human, ig_account, meta):
    content = make_publishable(db, human, content_type=ContentType.CAROUSEL)
    assert publish(db, human, content).status == "published"
    containers = list(meta.containers.values())
    assert [c.params.get("is_carousel_item") for c in containers] == ["true", "true", None]
    parent = containers[-1].params
    assert parent["media_type"] == "CAROUSEL"
    assert parent["children"] == ",".join(c.id for c in containers[:2])


def test_reels_waits_for_processing(db, human, ig_account, meta):
    meta.container_statuses = ["IN_PROGRESS", "IN_PROGRESS", "FINISHED"]
    content = make_publishable(db, human, content_type=ContentType.REELS)
    sleeps: list[float] = []
    result = service(db, sleeps).request_publish(
        content.id, human, expected_version=content.version
    )
    assert result.status == "published" and len(sleeps) == 2


# ================================================================== duplicates
def test_same_version_is_never_published_twice(db, human, ig_account, meta):
    content = make_publishable(db, human)
    publish(db, human, content)
    with pytest.raises(ConflictError):
        publish(db, human, content)
    schedule = db.scalars(select(ContentSchedule)).one()
    assert PublishService(db).execute(schedule.id).status == "skipped"
    assert meta.publish_calls == 1 and len(meta.published) == 1


def test_claim_is_exclusive(db, human, ig_account, meta):
    content = make_publishable(db, human)
    ScheduleService(db).schedule(content.id, human, scheduled_at=utcnow())
    schedule = db.scalars(select(ContentSchedule)).one()
    svc = PublishService(db)
    assert svc._claim(schedule.id) is True
    assert svc._claim(schedule.id) is False  # a second worker gets nothing
    assert svc.execute(schedule.id).status == "skipped"
    assert meta.requests == []


def test_lost_response_after_publish_is_reconciled_not_republished(db, human, ig_account, meta):
    meta.publish_behavior = "lost_after_publish"
    content = make_publishable(db, human)
    result = publish(db, human, content)
    assert result.status == "published", result.message
    db.expire_all()
    c = ContentService(db).get(content.id)
    assert c.status == ContentStatus.PUBLISHED
    assert c.ig_media_id == next(iter(meta.media))  # found via recent media (same caption)
    assert meta.publish_calls == 1 and len(meta.published) == 1
    assert AuditAction.CONTENT_PUBLISH_RECONCILED.value in actions(db, content.id)


def test_unknown_outcome_waits_then_reuses_the_same_container(db, human, ig_account, meta):
    meta.publish_behavior = "lost_before_publish"
    content = make_publishable(db, human)
    result = publish(db, human, content)
    assert result.status == "in_progress"
    db.expire_all()
    schedule = db.scalars(select(ContentSchedule)).one()
    assert schedule.outcome_unknown and schedule.status == ScheduleStatus.PROCESSING
    assert ContentService(db).get(content.id).status == ContentStatus.PUBLISHING
    with pytest.raises(ConflictError):  # no second publish while the outcome is unknown
        publish(db, human, ContentService(db).get(content.id))
    assert PublishService(db).reconcile_stale() == {"stale": 0}  # not stale yet

    db.execute(
        update(ContentSchedule).values(processing_started_at=utcnow() - timedelta(minutes=30))
    )
    db.commit()
    outcome = PublishService(db).reconcile_stale()
    assert outcome.get("published") == 1
    assert len(meta.containers) == 1  # reused, never re-created
    assert len(meta.published) == 1
    db.expire_all()
    assert ContentService(db).get(content.id).status == ContentStatus.PUBLISHED


def test_unknown_outcome_with_expired_container_fails_safely(db, human, ig_account, meta):
    meta.publish_behavior = "lost_before_publish"
    content = make_publishable(db, human)
    assert publish(db, human, content).status == "in_progress"
    container = next(iter(meta.containers.values()))
    container.statuses = ["EXPIRED"]
    db.execute(
        update(ContentSchedule).values(processing_started_at=utcnow() - timedelta(minutes=30))
    )
    db.commit()
    assert PublishService(db).reconcile_stale().get("failed") == 1
    db.expire_all()
    c = ContentService(db).get(content.id)
    assert c.status == ContentStatus.FAILED and "nashr qilinmagan" in c.last_error
    assert meta.published == []


def test_connect_error_is_retried_later_with_same_container(db, human, ig_account, meta):
    meta.publish_behavior = "connect_error"
    content = make_publishable(db, human)
    result = publish(db, human, content)
    assert result.status == "failed" and "qayta urinish" in result.message
    db.expire_all()
    schedule = db.scalars(select(ContentSchedule)).one()
    assert schedule.status == ScheduleStatus.PENDING and schedule.scheduled_at > utcnow()
    assert ContentService(db).get(content.id).status == ContentStatus.FAILED
    assert PublishService(db).process_due()["processed"] == 0  # not due yet

    meta.publish_behavior = "ok"
    db.execute(update(ContentSchedule).values(scheduled_at=utcnow() - timedelta(seconds=1)))
    db.commit()
    assert PublishService(db).process_due().get("published") == 1
    assert len(meta.containers) == 1 and len(meta.published) == 1


# ================================================================== failures
def test_container_error_fails_and_retry_creates_new_container(db, human, ig_account, meta):
    meta.container_statuses = ["ERROR"]
    content = make_publishable(db, human)
    result = publish(db, human, content)
    assert result.status == "failed"
    db.expire_all()
    c = ContentService(db).get(content.id)
    assert c.status == ContentStatus.FAILED and "Media" in c.last_error
    assert db.scalars(select(ContentSchedule)).one().ig_container_id is None

    meta.container_statuses = ["FINISHED"]
    assert publish(db, human, c).status == "published"  # human retry, same approval
    assert len(meta.containers) == 2 and len(meta.published) == 1


def test_expired_token_error_is_final_and_friendly(db, human, ig_account, meta):
    meta.publish_behavior = {
        "error": {
            "message": "Error validating access token",
            "type": "OAuthException",
            "code": 190,
            "error_subcode": 463,
        }
    }
    content = make_publishable(db, human)
    result = publish(db, human, content)
    assert result.status == "failed" and "qayta ulang" in result.message
    db.expire_all()
    assert db.scalars(select(ContentSchedule)).one().status == ScheduleStatus.FAILED


def test_rate_limit_defers_before_anything_is_created(db, human, ig_account, meta):
    meta.quota_usage = 100
    content = make_publishable(db, human)
    result = publish(db, human, content)
    assert result.status == "deferred" and "limit" in result.message
    assert meta.containers == {}
    db.expire_all()
    assert ContentService(db).get(content.id).status == ContentStatus.SCHEDULED
    schedule = db.scalars(select(ContentSchedule)).one()
    assert schedule.status == ScheduleStatus.PENDING
    assert schedule.scheduled_at > utcnow() + timedelta(minutes=50)


def test_quota_falls_back_when_meta_omits_total(db, human, ig_account, meta, monkeypatch):
    meta.quota_total = None
    meta.quota_usage = 3
    monkeypatch.setattr(get_settings(), "meta_publish_limit_fallback", 3)
    content = make_publishable(db, human)
    assert publish(db, human, content).status == "deferred"


def test_publish_limit_subcode_is_rate_limit():
    assert classify(9, 2207042, None) == MetaErrorKind.RATE_LIMIT
    assert classify(9004, 2207026, None) == MetaErrorKind.MEDIA_VALIDATION


# ================================================================== the gate
def test_preflight_blocks_without_calling_meta(db, human, ig_account, meta):
    content = make_publishable(db, human, media=[])  # no media
    result = publish(db, human, content)
    assert result.status == "failed" and "Media" in result.message
    assert meta.requests == []
    db.expire_all()
    assert ContentService(db).get(content.id).status == ContentStatus.FAILED


def test_requires_human_approver_and_valid_approval(db, human, viewer, agent, ig_account, meta):
    content = make_publishable(db, human)
    with pytest.raises(ApprovalForbiddenError):
        PublishService(db).request_publish(content.id, viewer, expected_version=content.version)
    with pytest.raises(ApprovalForbiddenError):
        PublishService(db).request_publish(content.id, agent, expected_version=content.version)
    ApprovalService(db).revoke(content.id, human, expected_version=content.version)
    with pytest.raises(ApprovalRequiredError):
        publish(db, human, ContentService(db).get(content.id))
    assert meta.requests == []
    denied = db.scalars(
        select(AuditLog).where(AuditLog.action == AuditAction.STATE_TRANSITION_DENIED.value)
    ).all()
    assert len(denied) == 2


def test_edit_after_scheduling_cancels_publish(db, human, ig_account, meta):
    content = make_publishable(db, human)
    ScheduleService(db).schedule(content.id, human, scheduled_at=utcnow())
    content = ContentService(db).get(content.id)
    ContentService(db).update(
        content.id, human, expected_version=content.version, changes={"caption": "Boshqa matn"}
    )
    assert PublishService(db).process_due()["processed"] == 0
    assert meta.requests == []


def test_approval_revoked_after_claim_is_caught(db, human, ig_account, meta):
    content = make_publishable(db, human)
    ScheduleService(db).schedule(content.id, human, scheduled_at=utcnow())
    schedule = db.scalars(select(ContentSchedule)).one()
    # Simulate a stale queued job: the approval disappears behind the scheduler's back.
    from app.models import Approval

    db.execute(update(Approval).values(invalidated_at=utcnow(), invalidation_reason="test"))
    db.commit()
    result = PublishService(db).execute(schedule.id)
    assert result.status == "failed"
    assert meta.requests == []


def test_agent_cannot_reach_publish_states(db, human, ig_account):
    content = make_publishable(db, human)
    rogue = AgentActor(name="content_creator", tools=frozenset())
    with pytest.raises(PermissionDeniedError):
        ContentService(db).start_publishing(content.id, rogue)
    with pytest.raises(PermissionDeniedError):
        ContentService(db).mark_published(content.id, rogue, ig_media_id="x")


def test_scheduled_publish_happens_only_when_due(db, human, ig_account, meta):
    content = make_publishable(db, human)
    ScheduleService(db).schedule(content.id, human, scheduled_at=utcnow() + timedelta(hours=2))
    assert PublishService(db).process_due() == {"due": 0, "processed": 0}
    db.execute(update(ContentSchedule).values(scheduled_at=utcnow() - timedelta(minutes=1)))
    db.commit()
    assert PublishService(db).process_due().get("published") == 1


def test_tokens_never_leak(db, human, ig_account, meta, caplog):
    caplog.set_level(logging.DEBUG)
    meta.publish_behavior = {
        "error": {"message": "Some Meta error", "type": "OAuthException", "code": 100}
    }
    content = make_publishable(db, human)
    publish(db, human, content)
    assert PUBLISH_TOKEN not in caplog.text
    for row in db.scalars(select(AuditLog)):
        assert PUBLISH_TOKEN not in str(row.details) and PUBLISH_TOKEN not in (row.error or "")
    db.expire_all()
    assert PUBLISH_TOKEN not in (ContentService(db).get(content.id).last_error or "")


# ================================================================== readiness
def test_readiness_publish_specific_checks(db, human, user, ig_account):
    content = make_publishable(db, human, media=[("IMAGE", "https://cdn.example/a.png")])
    checks = {c.key: c for c in ReviewService(db).readiness(content.id).checks}
    assert not checks["media_format"].ok
    assert checks["publish_permission"].ok and checks["publisher"].ok

    db.add(InstagramAccount(user_id=user.id, ig_user_id="second"))
    db.commit()
    from app.services.instagram import InstagramAccountService

    second = db.scalars(
        select(InstagramAccount).where(InstagramAccount.ig_user_id == "second")
    ).one()
    from app.core.actors import SystemActor

    InstagramAccountService(db).store_token(
        second.id, SystemActor("t"), access_token="t2", expires_at=utcnow() + timedelta(days=9)
    )
    # The account was pinned when the content was approved: a second connection
    # does not make it ambiguous (nor silently redirect it).
    checks = {c.key: c for c in ReviewService(db).readiness(content.id).checks}
    assert (
        checks["instagram_account"].ok
        and "@muxriddin.design" in checks["instagram_account"].message
    )
    unpinned = make_ready(db, human)
    checks = {c.key: c for c in ReviewService(db).readiness(unpinned.id).checks}
    assert (
        not checks["instagram_account"].ok
        and "akkauntni tanlang" in checks["instagram_account"].message
    )


def test_creator_story_is_a_warning_not_a_block(db, human, ig_account):
    ig_account.account_type = InstagramAccountType.CREATOR
    db.commit()
    content = make_publishable(db, human, content_type=ContentType.STORY)
    r = ReviewService(db).readiness(content.id)
    checks = {c.key: c for c in r.checks}
    assert checks["account_type"].severity == "warning" and r.ready


# ================================================================== API
def test_api_publish_preview_and_publish(api, db, human, ig_account, meta):
    content = make_publishable(db, human)
    p = api.get(f"/api/v1/contents/{content.id}/publish-preview").json()
    assert p["ready"] and p["plan"]["steps"][0]["params"]["image_url"]
    assert PUBLISH_TOKEN not in str(p)
    r = api.post(
        f"/api/v1/contents/{content.id}/publish", json={"expected_version": content.version}
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["status"] == "published"
    assert body["content"]["status"] == "PUBLISHED" and body["content"]["ig_permalink"]
    assert body["publish_state"]["status"] == "DONE"
    again = api.post(
        f"/api/v1/contents/{content.id}/publish", json={"expected_version": content.version}
    )
    assert again.status_code == 409
    assert meta.publish_calls == 1


def test_api_publish_stale_version(api, db, human, ig_account, meta):
    content = make_publishable(db, human)
    r = api.post(
        f"/api/v1/contents/{content.id}/publish", json={"expected_version": content.version - 1}
    )
    assert r.status_code == 409 and r.json()["error"]["code"] == "version_mismatch"


def test_api_publishing_limit_and_capabilities(api, db, human, ig_account, meta):
    meta.quota_usage = 7
    r = api.get(f"/api/v1/instagram/accounts/{ig_account.id}/publishing-limit").json()
    assert r == {
        "instagram_account_id": ig_account.id,
        "username": "muxriddin.design",
        "quota_usage": 7,
        "quota_total": 100,
        "remaining": 93,
        "quota_duration_seconds": 86400,
        "from_meta": True,
    }
    caps = api.get("/api/v1/instagram/capabilities").json()
    music = next(c for c in caps if c["key"] == "music")
    assert music == {
        "key": "music",
        "label": "Musiqa qo‘shish",
        "supported": False,
        "note": "Not supported by current Meta API",
    }


def test_telegram_is_told_about_publish_result(db, human, linked_owner, ig_account, meta):
    from app.services.telegram import TelegramService

    TelegramService(db).init_notify_cursor()
    content = make_publishable(db, human)
    publish(db, human, content)
    messages, _ = TelegramService(db).collect_review_notifications()
    texts = [m.text for _, m in messages]
    assert any("nashr qilindi" in t and "instagram.com/p/" in t for t in texts)


# ================================================================== review fixes
def test_unschedule_after_a_worker_claimed_it_does_not_publish(db, human, ig_account, meta):
    content = make_publishable(db, human)
    ScheduleService(db).schedule(content.id, human, scheduled_at=utcnow())
    schedule = db.scalars(select(ContentSchedule)).one()
    worker = PublishService(db)
    assert worker._claim(schedule.id)  # the worker has the row...
    ScheduleService(db).unschedule(content.id, human)  # ...when the human cancels
    result = worker._run(schedule.id)
    assert result.status == "failed" and "bekor" in result.message
    assert meta.published == [] and meta.containers == {}
    db.expire_all()
    assert ContentService(db).get(content.id).status == ContentStatus.APPROVED
    assert db.get(ContentSchedule, schedule.id).status == ScheduleStatus.FAILED


def test_reconcile_survives_a_missing_token(db, human, ig_account, meta):
    from app.models import OAuthToken

    meta.publish_behavior = "lost_before_publish"
    content = make_publishable(db, human)
    assert publish(db, human, content).status == "in_progress"
    db.execute(delete(OAuthToken))  # account disconnected / deauthorized meanwhile
    db.execute(
        update(ContentSchedule).values(processing_started_at=utcnow() - timedelta(minutes=30))
    )
    db.commit()
    assert PublishService(db).reconcile_stale() == {"stale": 1, "failed": 1}
    db.expire_all()
    c = ContentService(db).get(content.id)
    assert c.status == ContentStatus.FAILED and "Instagram’da tekshiring" in c.last_error
    assert db.scalars(select(ContentSchedule)).one().status == ScheduleStatus.FAILED


def test_approval_pins_the_account_and_moving_it_needs_a_new_approval(db, human, ig_account):
    content = make_publishable(db, human)
    assert content.instagram_account_id == ig_account.id  # recorded at approval time
    approved_version = content.version
    ContentService(db).update(
        content.id, human, expected_version=content.version, changes={"instagram_account_id": None}
    )
    db.expire_all()
    c = ContentService(db).get(content.id)
    assert c.version == approved_version + 1 and c.status == ContentStatus.READY_FOR_REVIEW
    assert ApprovalService(db).get_valid_approval(c) is None


def test_expired_approval_sends_scheduled_content_back_to_review(
    db, human, ig_account, meta, monkeypatch, publish_settings
):
    from app.models import Approval

    content = make_publishable(db, human)
    ScheduleService(db).schedule(content.id, human, scheduled_at=utcnow())
    db.execute(update(Approval).values(created_at=utcnow() - timedelta(hours=48)))
    db.commit()
    monkeypatch.setattr(publish_settings, "approval_max_age_hours", 24)
    assert PublishService(db).process_due() == {"due": 1, "processed": 1, "failed": 1}
    assert meta.published == []
    db.expire_all()
    c = ContentService(db).get(content.id)
    assert c.status == ContentStatus.READY_FOR_REVIEW  # can be approved again
    ApprovalService(db).approve(c.id, human, expected_version=c.version)
    assert ApprovalService(db).get_valid_approval(c) is not None


def test_quota_deferral_does_not_use_up_attempts(db, human, ig_account, meta):
    meta.quota_usage = meta.quota_total = 25
    content = make_publishable(db, human)
    assert publish(db, human, content).status == "deferred"
    assert db.scalars(select(ContentSchedule)).one().attempts == 0
