from datetime import timedelta

import pytest
from sqlalchemy import func, select

from app.core.actors import SystemActor
from app.core.crypto import TokenCipher
from app.core.errors import PermissionDeniedError
from app.core.transaction import atomic
from app.models import AuditLog, Content, ContentVersion, OAuthToken
from app.models.base import utcnow
from app.models.enums import AuditAction, ContentType
from app.services import AuditLogService, ContentService, InstagramAccountService
from app.services.audit import REDACTED, sanitize
from tests.conftest import make_approved

FAKE_TOKEN = "IGAAtest-plaintext-token-value-123"


def test_sanitize_redacts_nested_secrets():
    data = {
        "password": "p",
        "nested": {"access_token": "t", "refresh_token": "r", "ok": 1},
        "list": [{"Authorization": "Bearer x"}, {"jwt_secret_key": "s"}],
        "encryption_key": "k",
        "idempotency_key": "publish:content:1:v1",
        "caption": "hello",
    }
    clean = sanitize(data)
    assert clean["password"] == REDACTED
    assert clean["nested"]["access_token"] == REDACTED
    assert clean["nested"]["refresh_token"] == REDACTED
    assert clean["nested"]["ok"] == 1
    assert clean["list"][0]["Authorization"] == REDACTED
    assert clean["list"][1]["jwt_secret_key"] == REDACTED
    assert clean["encryption_key"] == REDACTED
    assert clean["idempotency_key"] == "publish:content:1:v1"
    assert clean["caption"] == "hello"


def test_audit_record_redacts(db, human):
    entry = AuditLogService(db).record(
        AuditAction.CONTENT_UPDATED, human, details={"password": "hunter2", "x": 1}
    )
    db.commit()
    assert entry.details == {"password": REDACTED, "x": 1}
    assert entry.actor_user_id == human.user_id


def test_full_lifecycle_audit_trail(db, human, publisher):
    content = make_approved(db, human)
    service = ContentService(db)
    service.start_publishing(content.id, publisher)
    service.mark_publish_failed(content.id, publisher, error="boom")
    actions = [
        e.action
        for e in db.scalars(
            select(AuditLog).where(AuditLog.content_id == content.id).order_by(AuditLog.id)
        )
    ]
    assert actions == [
        "CONTENT_CREATED",
        "CONTENT_VERSION_CREATED",
        "CONTENT_SUBMITTED_FOR_REVIEW",
        "CONTENT_APPROVED",
        "CONTENT_PUBLISH_STARTED",
        "CONTENT_PUBLISH_FAILED",
    ]
    for event in db.scalars(select(AuditLog).where(AuditLog.content_id == content.id)):
        assert event.timestamp is not None
        assert event.actor_type is not None
        assert event.content_version == 1
        assert event.status in {"SUCCESS", "FAILED"}


def test_tokens_never_reach_audit_or_plain_columns(db, user, human):
    service = InstagramAccountService(db)
    account = service.link_account(human, ig_user_id="ig-99", username="muxriddin")
    service.store_token(
        account.id,
        human,
        access_token=FAKE_TOKEN,
        expires_at=utcnow() + timedelta(days=60),
        scopes=["a", "b"],
    )
    for event in db.scalars(select(AuditLog)):
        assert FAKE_TOKEN not in str(event.details)
        assert FAKE_TOKEN not in (event.error or "")
    token = db.scalars(select(OAuthToken)).one()
    assert FAKE_TOKEN not in token.token_ciphertext
    assert TokenCipher.from_settings().decrypt(token.token_ciphertext) == FAKE_TOKEN
    assert service.get_access_token(account.id, SystemActor("publish_service")) == FAKE_TOKEN


def test_password_hash_never_in_audit(db, human, user):
    make_approved(db, human)
    for event in db.scalars(select(AuditLog)):
        assert user.password_hash not in str(event.details)


def test_failed_operation_rolls_back_everything(db, human):
    service = ContentService(db)
    before = db.scalar(select(func.count()).select_from(Content))
    with pytest.raises(PermissionDeniedError):
        with atomic(db):
            service.create(human, content_type=ContentType.POST, caption="will vanish")
            raise PermissionDeniedError("boom")
    assert db.scalar(select(func.count()).select_from(Content)) == before
    assert db.scalar(select(func.count()).select_from(ContentVersion)) == 0
    assert db.scalar(select(func.count()).select_from(AuditLog)) == 0


def test_nested_atomic_commits_once(db, human):
    service = ContentService(db)
    with atomic(db):
        a = service.create(human, content_type=ContentType.POST, caption="a")
        b = service.create(human, content_type=ContentType.POST, caption="b")
    db.rollback()  # nothing pending: both were committed by the outer block
    assert service.get(a.id) and service.get(b.id)


def test_error_inside_service_leaves_no_partial_version(db, human, monkeypatch):
    content = make_approved(db, human)
    service = ContentService(db)

    def explode(*args, **kwargs):
        raise RuntimeError("disk full")

    monkeypatch.setattr("app.services.content.cancel_pending_schedules", explode)
    with pytest.raises(RuntimeError):
        service.update(content.id, human, expected_version=1, changes={"caption": "x"})
    db.expire_all()
    fresh = service.get(content.id)
    assert fresh.version == 1 and fresh.caption != "x"
    assert service.is_publish_authorized(fresh)  # approval not invalidated
