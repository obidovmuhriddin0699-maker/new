from datetime import timedelta

import pytest

from app.core.actors import AgentActor, SystemActor
from app.core.errors import ConflictError, PermissionDeniedError
from app.models.base import utcnow
from app.models.enums import AIJobStatus
from app.services import AIJobService, BrandProfileService, InstagramAccountService


def test_brand_profile_service(db, human, agent):
    service = BrandProfileService(db)
    a = service.create(human, name="Muxriddin Design", voice=["Premium"], make_default=True)
    b = service.create(human, name="Other")
    assert service.get_default().id == a.id
    service.set_default(b.id, human)
    assert service.get_default().id == b.id
    service.update(a.id, human, voice=["Minimal"])
    assert a.voice == ["Minimal"]
    with pytest.raises(ConflictError):
        service.create(human, name="Other")
    with pytest.raises(PermissionDeniedError):
        service.create(agent, name="Agent brand")


def test_ai_job_lifecycle(db, agent, human):
    service = AIJobService(db)
    job = service.create(
        agent,
        agent="planner",
        input={"prompt": "x", "api_key": "secret"},
        provider="ollama",
        model="qwen2.5:3b",
    )
    assert job.input["api_key"] == "***REDACTED***"
    service.start(job.id, agent)
    service.succeed(job.id, agent, output={"text": "ok"})
    assert job.status == AIJobStatus.SUCCEEDED and job.duration_ms is not None
    with pytest.raises(ConflictError):
        service.fail(job.id, agent, error="late")
    with pytest.raises(PermissionDeniedError):
        service.create(human, agent="planner", input={})


def test_instagram_account_service(db, human, viewer, agent):
    service = InstagramAccountService(db)
    account = service.link_account(human, ig_user_id="ig-1", username="muxriddin")
    with pytest.raises(PermissionDeniedError):
        service.link_account(viewer, ig_user_id="ig-2", username="v")
    with pytest.raises(PermissionDeniedError):
        service.store_token(account.id, agent, access_token="t", expires_at=None)
    service.store_token(account.id, human, access_token="t1", expires_at=None)
    service.store_token(account.id, human, access_token="t2", expires_at=None)
    system = SystemActor("publish_service")
    assert service.get_access_token(account.id, system) == "t2"  # old token revoked
    with pytest.raises(PermissionDeniedError):
        service.get_access_token(account.id, human)
    with pytest.raises(PermissionDeniedError):
        service.get_access_token(account.id, AgentActor(name="x"))
    service.disconnect(account.id, human)
    assert service.get_access_token(account.id, system) is None
    # Reconnecting restores the soft-deleted record.
    again = service.link_account(human, ig_user_id="ig-1", username="muxriddin")
    assert again.id == account.id and again.deleted_at is None


def test_expired_token_is_not_returned(db, human):
    service = InstagramAccountService(db)
    account = service.link_account(human, ig_user_id="ig-3", username="m")
    service.store_token(
        account.id, human, access_token="t", expires_at=utcnow() - timedelta(minutes=1)
    )
    assert service.get_access_token(account.id, SystemActor("insights")) is None
