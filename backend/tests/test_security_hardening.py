"""PHASE 10: rate limiting, login protection, session revocation, headers, body limits,
audit immutability, client-IP trust."""

import pytest
from sqlalchemy import select, text, update
from sqlalchemy.exc import DatabaseError

from app.core.config import get_settings
from app.core.ratelimit import (
    LOGIN_ACCOUNT_FAILURES,
    LOGIN_FAILURES,
    Limit,
    RateLimiter,
    get_limiter,
)
from app.models import AuditLog, User
from app.models.enums import AuditAction
from tests.conftest import TEST_PASSWORD

LOGIN = "/api/v1/auth/login"


def login(client, password=TEST_PASSWORD, email="owner@example.com", headers=None):
    return client.post(LOGIN, json={"email": email, "password": password}, headers=headers or {})


def bearer(resp) -> dict[str, str]:
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


# ================================================================== limiter core
def test_fixed_window_and_reset():
    limiter = RateLimiter("memory")
    rule = Limit("t", 3, 60)
    assert [limiter.hit(rule, "k")[0] for _ in range(4)] == [True, True, True, False]
    assert limiter.hit(rule, "other")[0] is True  # keys are independent
    limiter.reset(rule, "k")
    assert limiter.hit(rule, "k")[0] is True


def test_redis_backend_and_outage_fallback(monkeypatch):
    redis = pytest.importorskip("redis")
    client = redis.Redis.from_url("redis://127.0.0.1:6379/15", socket_connect_timeout=0.5)
    try:
        client.ping()
    except Exception:  # noqa: BLE001
        pytest.skip("local Redis not running")
    client.flushdb()
    limiter = RateLimiter("redis")
    limiter._redis = client
    rule = Limit("redis-test", 2, 60)
    assert [limiter.hit(rule, "x")[0] for _ in range(3)] == [True, True, False]
    assert 0 < client.ttl(next(iter(client.scan_iter("rl:redis-test:*")))) <= 60

    class Broken:
        def pipeline(self):
            raise ConnectionError("down")

    limiter._redis = Broken()
    # Redis down: falls back to (stricter, per-process) memory counting, never fails open.
    assert [limiter.hit(rule, "y")[0] for _ in range(3)] == [True, True, False]
    client.flushdb()


# ================================================================== login protection
def test_login_lockout_after_repeated_failures(client, user, db):
    for _ in range(LOGIN_FAILURES.limit):
        assert login(client, "wrong-password-xx").status_code == 401
    blocked = login(client)  # even the right password is refused during the lockout
    assert blocked.status_code == 429
    assert int(blocked.headers["Retry-After"]) > 0
    assert blocked.json()["error"]["code"] == "rate_limited"
    actions = [a.action for a in db.scalars(select(AuditLog))]
    assert actions.count(AuditAction.AUTH_LOGIN_FAILED.value) == LOGIN_FAILURES.limit
    assert AuditAction.AUTH_LOGIN_BLOCKED.value in actions


def test_success_resets_failures_and_is_audited(client, user, db):
    for _ in range(LOGIN_FAILURES.limit - 1):
        login(client, "wrong-password-xx")
    assert login(client).status_code == 200
    for _ in range(LOGIN_FAILURES.limit - 1):
        login(client, "wrong-password-xx")
    assert login(client).status_code == 200  # counter was reset by the success
    ok = db.scalars(
        select(AuditLog).where(AuditLog.action == AuditAction.AUTH_LOGIN_SUCCEEDED.value)
    ).first()
    assert ok.actor_user_id == user.id
    failed = db.scalars(
        select(AuditLog).where(AuditLog.action == AuditAction.AUTH_LOGIN_FAILED.value)
    ).first()
    assert failed.details["email"] == "owner@example.com"
    assert TEST_PASSWORD not in str(failed.details) and "wrong-password" not in str(failed.details)


def test_unknown_email_is_indistinguishable(client, user):
    a = login(client, "wrong-password-xx")
    b = login(client, email="nobody@example.com")
    assert a.status_code == b.status_code == 401
    assert a.json()["error"]["message"] == b.json()["error"]["message"]


def test_spoofed_forwarded_for_does_not_bypass_lockout(client, user):
    # TestClient's peer ("testclient") is not a trusted proxy, so X-Forwarded-For is ignored.
    for _ in range(LOGIN_FAILURES.limit):
        login(client, "wrong-password-xx", headers={"X-Forwarded-For": "203.0.113.9"})
    assert login(client, headers={"X-Forwarded-For": "198.51.100.7"}).status_code == 429


def test_client_ip_only_trusts_configured_proxies(monkeypatch):
    from starlette.requests import Request

    from app.core.ratelimit import client_ip

    def req(peer, xff):
        scope = {
            "type": "http",
            "client": (peer, 1),
            "headers": [(b"x-forwarded-for", xff.encode())],
        }
        return Request(scope)

    monkeypatch.setattr(get_settings(), "trusted_proxies", ["127.0.0.1", "10.0.0.0/8"])
    assert client_ip(req("127.0.0.1", "203.0.113.9")) == "203.0.113.9"
    # Spoofed left-most entry is ignored: the right-most untrusted hop is the client.
    assert client_ip(req("127.0.0.1", "1.1.1.1, 203.0.113.9, 10.0.0.5")) == "203.0.113.9"
    assert client_ip(req("198.51.100.1", "203.0.113.9")) == "198.51.100.1"  # untrusted peer


# ================================================================== sessions
def test_logout_revokes_the_token(client, user):
    r = login(client)
    headers = bearer(r)
    assert client.get("/api/v1/auth/me", headers=headers).status_code == 200
    assert client.post("/api/v1/auth/logout", headers=headers).status_code == 204
    gone = client.get("/api/v1/auth/me", headers=headers)
    assert gone.status_code == 401 and gone.json()["error"]["code"] == "session_revoked"


def test_logout_all_revokes_every_session_but_allows_new_login(client, user):
    a, b = bearer(login(client)), bearer(login(client))
    assert client.post("/api/v1/auth/logout-all", headers=a).status_code == 204
    assert client.get("/api/v1/auth/me", headers=a).status_code == 401
    assert client.get("/api/v1/auth/me", headers=b).status_code == 401
    fresh = bearer(login(client))  # immediately after: millisecond cut-off, no false reject
    assert client.get("/api/v1/auth/me", headers=fresh).status_code == 200


def test_change_password(client, user, db):
    headers = bearer(login(client))
    weak = client.post(
        "/api/v1/auth/change-password",
        json={"current_password": TEST_PASSWORD, "new_password": "owner-owner-1234"},
        headers=headers,
    )
    assert weak.status_code == 400 and weak.json()["error"]["code"] == "weak_password"
    wrong = client.post(
        "/api/v1/auth/change-password",
        json={"current_password": "nope-nope-nope", "new_password": "N3w-strong-passphrase"},
        headers=headers,
    )
    assert wrong.status_code == 400  # not 401: a typo must not end the session
    ok = client.post(
        "/api/v1/auth/change-password",
        json={"current_password": TEST_PASSWORD, "new_password": "N3w-strong-passphrase"},
        headers=headers,
    )
    assert ok.status_code == 204
    assert client.get("/api/v1/auth/me", headers=headers).status_code == 401  # all signed out
    assert login(client).status_code == 401
    assert login(client, "N3w-strong-passphrase").status_code == 200
    db.expire_all()
    assert db.get(User, user.id).password_changed_at is not None


def test_deactivated_user_token_stops_working(client, user, db):
    headers = bearer(login(client))
    db.execute(update(User).values(is_active=False))
    db.commit()
    assert client.get("/api/v1/auth/me", headers=headers).status_code == 401


# ================================================================== endpoint limits
def test_publish_endpoint_is_rate_limited(client, auth_headers):
    from app.core.ratelimit import PUBLISH

    user_id = client.get("/api/v1/auth/me", headers=auth_headers).json()["id"]
    for _ in range(PUBLISH.limit):
        get_limiter().hit(PUBLISH, f"user:{user_id}")
    r = client.post(
        "/api/v1/contents/1/publish", json={"expected_version": 1}, headers=auth_headers
    )
    assert r.status_code == 429 and r.headers["Retry-After"]


def test_global_per_ip_limit(client, monkeypatch):
    from app.core import ratelimit

    limiter = get_limiter()
    for _ in range(ratelimit.API_IP.limit):
        limiter.hit(ratelimit.API_IP, "ip:testclient")
    r = client.get("/api/v1/auth/me")
    assert r.status_code == 429
    assert client.get("/health").status_code in (200, 503)  # health is never limited


def test_rate_limit_can_be_disabled_outside_production(client, user, monkeypatch):
    monkeypatch.setattr(get_settings(), "rate_limit_enabled", False)
    for _ in range(LOGIN_FAILURES.limit + 2):
        login(client, "wrong-password-xx")
    assert login(client).status_code == 200


# ================================================================== request hygiene
def test_security_headers(client):
    r = client.get("/api/v1/health")
    h = r.headers
    assert h["x-content-type-options"] == "nosniff" and h["x-frame-options"] == "DENY"
    assert "default-src 'none'" in h["content-security-policy"]
    assert h["cache-control"] == "no-store"
    assert h["cross-origin-resource-policy"] == "same-origin"
    assert "strict-transport-security" not in h  # only in production


def test_hsts_in_production(monkeypatch):
    from starlette.responses import Response

    from app.main import _security_headers

    class Req:
        class url:  # noqa: N801
            path = "/api/v1/x"

    resp = Response()
    _security_headers(Req(), resp, production=True)
    assert resp.headers["strict-transport-security"].startswith("max-age=31536000")


def test_request_id_is_sanitised(client):
    bad = client.get("/api/v1/health", headers={"X-Request-ID": "abc def<script>"})
    assert bad.headers["x-request-id"] != "abc def<script>"
    good = client.get("/api/v1/health", headers={"X-Request-ID": "req-123.ok_1"})
    assert good.headers["x-request-id"] == "req-123.ok_1"


def test_json_body_size_limit(client, auth_headers, monkeypatch):
    monkeypatch.setattr(get_settings(), "max_json_body_kb", 1)
    from fastapi.testclient import TestClient

    from app.main import create_app

    with TestClient(create_app()) as c:
        r = c.post(
            LOGIN, content=b"{" + b" " * 5000 + b"}", headers={"Content-Type": "application/json"}
        )
    assert r.status_code == 413 and r.json()["error"]["code"] == "body_too_large"


def test_trusted_hosts(monkeypatch):
    monkeypatch.setattr(get_settings(), "allowed_hosts", ["panel.example.com"])
    from fastapi.testclient import TestClient

    from app.main import create_app

    with TestClient(create_app(), base_url="http://evil.example") as c:
        assert c.get("/api/v1/health").status_code == 400
    with TestClient(create_app(), base_url="http://panel.example.com") as c:
        assert c.get("/api/v1/health").status_code in (200, 503)


# ================================================================== audit immutability
def test_audit_log_is_append_only(db, human):
    from tests.conftest import make_content

    make_content(db, human)
    with pytest.raises(DatabaseError, match="append-only"):
        db.execute(update(AuditLog).values(action="TAMPERED"))
        db.flush()
    db.rollback()
    with pytest.raises(DatabaseError, match="append-only"):
        db.execute(text("DELETE FROM audit_logs"))
    db.rollback()
    assert db.scalars(select(AuditLog)).first().action != "TAMPERED"


def test_rotate_token_keys(db, ig_account, monkeypatch):
    from cryptography.fernet import Fernet
    from pydantic import SecretStr

    from app.cli import rotate_token_keys
    from app.core.crypto import TokenCipher
    from app.models import OAuthToken
    from tests.conftest import PUBLISH_TOKEN

    old = get_settings().token_encryption_keys.get_secret_value()
    new = Fernet.generate_key().decode()
    monkeypatch.setattr(get_settings(), "token_encryption_keys", SecretStr(f"{new},{old}"))
    assert rotate_token_keys() == 1
    db.expire_all()
    row = db.scalars(select(OAuthToken)).one()
    assert TokenCipher([new]).decrypt(row.token_ciphertext) == PUBLISH_TOKEN  # old key not needed
    assert PUBLISH_TOKEN not in row.token_ciphertext


def test_cli_commands_run_as_a_process(db):
    """Regression: functions defined after the __main__ guard worked when imported by
    tests but crashed as `python -m app.cli ...` (found by the PHASE 11 Docker smoke)."""
    import os
    import subprocess
    import sys
    from pathlib import Path

    backend = Path(__file__).resolve().parents[1]
    run = lambda *a, **env: subprocess.run(  # noqa: E731
        [sys.executable, "-m", "app.cli", *a],
        cwd=backend,
        capture_output=True,
        text=True,
        env={**os.environ, **env},
        timeout=60,
    )
    rotated = run("rotate-token-keys")
    assert rotated.returncode == 0, rotated.stderr
    assert "re-encrypted 0 token(s)" in rotated.stdout
    role = run("db-app-role", APP_DB_USER="", APP_DB_PASSWORD="")
    assert role.returncode == 2 and "APP_DB_USER" in role.stdout


# ================================================================== review fixes
def test_password_spraying_from_many_addresses_locks_the_account(db, user):
    from app.core.errors import AppError
    from app.services.auth import AuthService

    for i in range(LOGIN_ACCOUNT_FAILURES.limit):
        with pytest.raises(AppError):
            AuthService(db).login(user.email, "wrong-password-xx", ip=f"198.51.100.{i}")
    with pytest.raises(AppError) as exc:  # even the right password, from a fresh address
        AuthService(db).login(user.email, TEST_PASSWORD, ip="203.0.113.200")
    assert exc.value.code == "rate_limited"
    # Other accounts are unaffected.
    with pytest.raises(AppError) as other:
        AuthService(db).login("someone-else@example.com", "x" * 12, ip="203.0.113.201")
    assert other.value.code != "rate_limited"


def _viewer_headers(viewer) -> dict[str, str]:
    from app.core.security import create_access_token

    return {"Authorization": f"Bearer {create_access_token(str(viewer.user_id))}"}


def test_viewer_upload_is_refused_before_anything_is_stored(client, db, human, viewer):
    from pathlib import Path

    from tests.conftest import make_ready

    content = make_ready(db, human)
    media = Path(get_settings().media_root)
    before = set(media.glob("*")) if media.exists() else set()
    jpeg = b"\xff\xd8\xff\xe0" + b"\x00" * 64
    r = client.post(
        f"/api/v1/contents/{content.id}/assets/upload",
        params={"expected_version": content.version},
        content=jpeg,
        headers={**_viewer_headers(viewer), "Content-Type": "image/jpeg"},
    )
    assert r.status_code == 403
    after = set(media.glob("*")) if media.exists() else set()
    assert after == before


def test_viewer_cannot_write_evaluations_into_content_history(client, db, human, viewer):
    from tests.conftest import make_ready

    content = make_ready(db, human)
    r = client.post(
        "/api/v1/ai/evaluate-content",
        json={"content_id": content.id},
        headers=_viewer_headers(viewer),
    )
    assert r.status_code == 403
    assert not db.scalars(
        select(AuditLog).where(AuditLog.action == AuditAction.AI_CONTENT_EVALUATED.value)
    ).all()


def test_live_quota_lookups_are_rate_limited_per_user(client, auth_headers):
    from app.core.ratelimit import QUOTA_CHECK

    user_id = client.get("/api/v1/auth/me", headers=auth_headers).json()["id"]
    for _ in range(QUOTA_CHECK.limit):
        get_limiter().hit(QUOTA_CHECK, f"user:{user_id}")
    r = client.get("/api/v1/instagram/accounts/1/publishing-limit", headers=auth_headers)
    assert r.status_code == 429 and r.headers["Retry-After"]
