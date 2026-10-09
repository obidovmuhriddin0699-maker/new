from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import select, update

from app.core.actors import HumanActor
from app.core.errors import (
    ApprovalForbiddenError,
    ApprovalRequiredError,
    InvalidStateTransitionError,
    VersionMismatchError,
)
from app.core.security import hash_password
from app.models import Approval, AuditLog, InstagramAccount, OAuthToken, User
from app.models.base import utcnow
from app.models.enums import AssetKind, ContentStatus, UserRole
from app.services import (
    ApprovalService,
    AssetInput,
    ContentService,
    ScheduleService,
)
from app.services.review import ReviewService
from tests.conftest import TEST_PASSWORD, make_approved, make_content, make_ready


@pytest.fixture
def second_admin(db) -> HumanActor:
    u = User(
        email="second@example.com", password_hash=hash_password(TEST_PASSWORD), role=UserRole.ADMIN
    )
    db.add(u)
    db.commit()
    return HumanActor(user_id=u.id)


# ------------------------------------------------------------------ policies
def test_four_eyes_policy(db, human, second_admin, monkeypatch):
    from app.core.config import get_settings

    monkeypatch.setattr(get_settings(), "approval_require_different_approver", True)
    content = make_ready(db, human)  # v1 written by `human`
    with pytest.raises(ApprovalForbiddenError) as exc:
        ApprovalService(db).approve(content.id, human, expected_version=1)
    assert exc.value.code == "four_eyes_required"
    assert ApprovalService(db).approve(content.id, second_admin, expected_version=1).created


def test_four_eyes_allows_ai_written_versions(db, human, agent, monkeypatch):
    from app.core.config import get_settings

    monkeypatch.setattr(get_settings(), "approval_require_different_approver", True)
    content = make_content(db, agent)
    ContentService(db).submit_for_review(content.id, agent)
    assert ApprovalService(db).approve(content.id, human, expected_version=1).created


def test_four_eyes_off_by_default(db, human):
    content = make_ready(db, human)
    assert ApprovalService(db).approve(content.id, human, expected_version=1).created


def test_approval_expiry(db, human, publisher, monkeypatch):
    from app.core.config import get_settings

    content = make_approved(db, human)
    db.execute(update(Approval).values(created_at=utcnow() - timedelta(hours=50)))
    db.commit()
    assert ContentService(db).is_publish_authorized(content)  # default: no expiry
    monkeypatch.setattr(get_settings(), "approval_max_age_hours", 48)
    check = ApprovalService(db).evaluate(content)
    assert not check.valid and check.reasons == ("approval_expired",)
    with pytest.raises(ApprovalRequiredError) as exc:
        ContentService(db).start_publishing(content.id, publisher)
    assert exc.value.details["reasons"] == ["approval_expired"]


def test_evaluate_reports_reasons(db, human, user):
    content = make_ready(db, human)
    assert ApprovalService(db).evaluate(content).reasons == ("no_active_approval",)
    ApprovalService(db).approve(content.id, human, expected_version=1)
    user.role = UserRole.VIEWER
    db.commit()
    assert "approver_inactive" in ApprovalService(db).evaluate(content).reasons


# ------------------------------------------------------------------ revoke
def test_revoke_approval(db, human):
    content = make_approved(db, human)
    ScheduleService(db).schedule(content.id, human, scheduled_at=utcnow() + timedelta(days=1))
    ApprovalService(db).revoke(content.id, human, expected_version=1, comment="Kutib turamiz")
    assert content.status == ContentStatus.READY_FOR_REVIEW
    assert not ContentService(db).is_publish_authorized(content)
    assert content.schedules[0].status.value == "CANCELLED"
    approval = db.scalars(select(Approval)).one()
    assert approval.invalidation_reason == "revoked"
    event = db.scalars(select(AuditLog).where(AuditLog.action == "CONTENT_APPROVAL_REVOKED")).one()
    assert event.details["comment"] == "Kutib turamiz"
    # The same version can be approved again afterwards.
    assert ApprovalService(db).approve(content.id, human, expected_version=1).created


def test_revoke_rules(db, human, agent, viewer):
    content = make_ready(db, human)
    with pytest.raises(InvalidStateTransitionError):
        ApprovalService(db).revoke(content.id, human, expected_version=1)
    ApprovalService(db).approve(content.id, human, expected_version=1)
    with pytest.raises(VersionMismatchError):
        ApprovalService(db).revoke(content.id, human, expected_version=2)
    with pytest.raises(ApprovalForbiddenError):
        ApprovalService(db).revoke(content.id, agent, expected_version=1)
    with pytest.raises(ApprovalForbiddenError):
        ApprovalService(db).revoke(content.id, viewer, expected_version=1)
    denied = db.scalars(select(AuditLog).where(AuditLog.action == "APPROVAL_DENIED")).all()
    assert len(denied) >= 2


# ------------------------------------------------------------------ readiness
def _checks(r):
    return {c.key: c for c in r.checks}


def test_readiness_blocks_everything_today(db, human):
    content = make_ready(db, human)
    r = ReviewService(db).readiness(content.id)
    c = _checks(r)
    assert not r.ready
    assert not c["status"].ok and not c["approval"].ok
    assert not c["media"].ok and not c["instagram_account"].ok
    assert not c["publisher"].ok and "PHASE 8" in c["publisher"].message
    assert c["dry_run"].severity == "info"


def test_readiness_passes_all_but_publisher_when_prepared(db, human, user):
    content = make_content(db, human, aspect_ratio="4:5", cta="Saqlab qo‘ying")
    ContentService(db).add_asset(
        content.id,
        human,
        expected_version=1,
        asset=AssetInput(
            kind=AssetKind.IMAGE, public_url="https://cdn.example/a.jpg", width=1080, height=1350
        ),
    )
    ContentService(db).submit_for_review(content.id, human)
    ApprovalService(db).approve(content.id, human, expected_version=2)
    account = InstagramAccount(user_id=user.id, ig_user_id="ig-1")
    db.add(account)
    db.flush()
    db.add(
        OAuthToken(
            instagram_account_id=account.id,
            token_ciphertext="x",
            expires_at=datetime.now(UTC) + timedelta(days=30),
        )
    )
    db.commit()
    c = _checks(ReviewService(db).readiness(content.id))
    for key in (
        "status",
        "approval",
        "quality",
        "format",
        "media",
        "media_https",
        "instagram_account",
    ):
        assert c[key].ok, (key, c[key].message)
    assert not c["publisher"].ok  # honest: nothing can publish before PHASE 8


def test_readiness_detects_wrong_media(db, human):
    content = make_content(
        db,
        human,
        content_type=__import__("app.models.enums", fromlist=["ContentType"]).ContentType.REELS,
        aspect_ratio="4:5",
    )
    ContentService(db).add_asset(
        content.id,
        human,
        expected_version=1,
        asset=AssetInput(kind=AssetKind.IMAGE, public_url="http://insecure.example/a.jpg"),
    )
    c = _checks(ReviewService(db).readiness(content.id))
    assert not c["format"].ok and "9:16" in c["format"].message
    assert not c["media"].ok


def test_readiness_flags_quality_errors(db, human):
    content = make_content(db, human, caption="Natija 100% kafolat.")
    c = _checks(ReviewService(db).readiness(content.id))
    assert not c["quality"].ok and "guarantee_claim" in c["quality"].message


# ------------------------------------------------------------------ diff
def test_diff_against_last_approved_version(db, human):
    content = make_approved(db, human)
    service = ContentService(db)
    service.update(
        content.id,
        human,
        expected_version=1,
        changes={
            "caption": "Yangi birinchi qator\nIkkinchi qator",
            "hashtags": ["#interior", "#new"],
        },
    )
    service.update(content.id, human, expected_version=2, changes={"cta": "Yozing"})
    d = ReviewService(db).diff(content.id)
    assert (d.from_version, d.to_version) == (1, 3)
    assert d.from_label == "oxirgi tasdiqlangan versiya"
    assert set(d.changed_fields) == {"caption", "cta", "hashtags"}
    caption = next(f for f in d.fields if f.field == "caption")
    assert {"op": "add", "text": "Ikkinchi qator"} in caption.lines
    assert any(line["op"] == "remove" for line in caption.lines)
    tags = next(f for f in d.fields if f.field == "hashtags")
    assert tags.lines == [{"op": "add", "text": "#new"}]


def test_diff_defaults_to_previous_and_validates(db, human):
    from app.core.errors import AppError

    content = make_content(db, human)
    ContentService(db).update(content.id, human, expected_version=1, changes={"topic": "B"})
    d = ReviewService(db).diff(content.id)
    assert (d.from_version, d.to_version, d.from_label) == (1, 2, "oldingi versiya")
    assert d.changed_fields == ["topic"]
    with pytest.raises(AppError):
        ReviewService(db).diff(content.id, from_version=9)


# ------------------------------------------------------------------ API
@pytest.fixture
def api(client, auth_headers):
    client.headers.update(auth_headers)
    return client


def test_api_readiness_diff_revoke(api, db, human):
    content = make_approved(db, human)
    r = api.get(f"/api/v1/contents/{content.id}/readiness").json()
    assert r["ready"] is False and {c["key"] for c in r["checks"]} >= {"approval", "publisher"}
    assert next(c for c in r["checks"] if c["key"] == "approval")["ok"] is True
    api.patch(f"/api/v1/contents/{content.id}", json={"expected_version": 1, "caption": "B"})
    d = api.get(f"/api/v1/contents/{content.id}/diff").json()
    assert d["changed_fields"] == ["caption"] and d["from_version"] == 1
    assert api.get(f"/api/v1/contents/{content.id}/diff?from_version=7").status_code == 400
    api.post(f"/api/v1/contents/{content.id}/approve", json={"expected_version": 2})
    rv = api.post(
        f"/api/v1/contents/{content.id}/revoke-approval",
        json={"expected_version": 2, "comment": "x"},
    )
    assert rv.status_code == 200 and rv.json()["status"] == "READY_FOR_REVIEW"
    assert (
        api.post(
            f"/api/v1/contents/{content.id}/revoke-approval", json={"expected_version": 2}
        ).status_code
        == 409
    )


def test_api_approvals_log_and_waiting_sort(api, db, human):
    first = make_ready(db, human)
    second = make_ready(db, human)
    ApprovalService(db).approve(second.id, human, expected_version=1)
    ApprovalService(db).reject(first.id, human, expected_version=1, comment="no")
    log = api.get("/api/v1/approvals").json()
    assert log["total"] == 2
    assert log["items"][0]["decision"] == "REJECTED"
    assert log["items"][0]["decided_by_email"] == "owner@example.com"
    active = api.get("/api/v1/approvals?active_only=true").json()
    assert [i["content_id"] for i in active["items"]] == [second.id] and active["items"][0][
        "active"
    ]
    assert api.get("/api/v1/approvals?decision=EDIT_REQUESTED").json()["total"] == 0

    a, b = make_ready(db, human), make_ready(db, human)
    queue = api.get("/api/v1/contents?status=READY_FOR_REVIEW&sort=waiting").json()
    assert [i["id"] for i in queue["items"]] == [a.id, b.id]  # oldest first
    assert api.get("/api/v1/contents?sort=bogus").status_code == 422


@pytest.mark.parametrize(
    "path", ["/api/v1/approvals", "/api/v1/contents/1/readiness", "/api/v1/contents/1/diff"]
)
def test_requires_auth(client, path):
    assert client.get(path).status_code == 401
