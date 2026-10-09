import base64
import hashlib
import hmac
import json
import logging
from datetime import timedelta
from urllib.parse import parse_qs, urlparse

import httpx
import pytest
import respx
from sqlalchemy import select, update

from app.core.actors import SystemActor
from app.core.crypto import TokenCipher
from app.core.errors import AppError, PermissionDeniedError
from app.integrations.meta.errors import MetaApiError, MetaErrorKind, classify, from_response
from app.integrations.meta.instagram_login import strip_code
from app.models import (
    AnalyticsSnapshot,
    AuditLog,
    DataDeletionRequest,
    InstagramAccount,
    OAuthState,
    OAuthToken,
)
from app.models.base import utcnow
from app.models.enums import InstagramAccountType
from app.services.instagram_oauth import InstagramOAuthService
from app.services.review import ReviewService
from tests.conftest import FAKE_APP_SECRET, META, make_ready

SHORT, LONG, LONG2 = "IGAA-short-SECRET1", "IGAA-long-SECRET2", "IGAA-long-SECRET3"
IG_ID = "17841400000000001"
PERMS = (
    "instagram_business_basic,instagram_business_content_publish,instagram_business_manage_insights"
)


def mock_meta(
    *,
    perms: str = PERMS,
    account_type: str = "BUSINESS",
    flat: bool = False,
    long_status: int = 200,
):
    short_body = {"access_token": SHORT, "user_id": IG_ID, "permissions": perms}
    token = respx.post(META["token"]).mock(
        return_value=httpx.Response(200, json=short_body if flat else {"data": [short_body]})
    )
    exchange = respx.get(f"{META['graph']}/access_token").mock(
        return_value=httpx.Response(
            long_status,
            json={"access_token": LONG, "token_type": "bearer", "expires_in": 5184000}
            if long_status == 200
            else {
                "error": {
                    "message": "Error validating",
                    "type": "OAuthException",
                    "code": 190,
                    "fbtrace_id": "TRACE1",
                }
            },
        )
    )
    me = respx.get(f"{META['graph']}/v26.0/me").mock(
        return_value=httpx.Response(
            200,
            json={
                "user_id": IG_ID,
                "id": "app-scoped-9",
                "username": "muxriddin.design",
                "account_type": account_type,
            },
        )
    )
    return token, exchange, me


def start_state(db, human) -> str:
    url = InstagramOAuthService(db).start(human)
    return parse_qs(urlparse(url).query)["state"][0]


# ------------------------------------------------------------------ start
def test_start_builds_documented_authorize_url(db, human, meta_settings):
    url = InstagramOAuthService(db).start(human)
    parsed = urlparse(url)
    q = parse_qs(parsed.query)
    assert f"{parsed.scheme}://{parsed.netloc}{parsed.path}" == META["authorize"]
    assert q["client_id"] == ["123456"] and q["response_type"] == ["code"]
    assert q["redirect_uri"] == ["https://panel.example/instagram/callback"]
    assert q["scope"][0].split(",")[0] == "instagram_business_basic"
    assert len(q["state"][0]) >= 40
    assert FAKE_APP_SECRET not in url
    row = db.scalars(select(OAuthState)).one()
    assert row.state_hash != q["state"][0]  # only the hash is stored


def test_start_requires_configuration_and_writer(db, human, viewer):
    with pytest.raises(MetaApiError) as exc:
        InstagramOAuthService(db).start(human)
    assert exc.value.kind == MetaErrorKind.NOT_CONFIGURED and exc.value.status_code == 503


def test_start_requires_encryption_keys(db, human, meta_settings, monkeypatch):
    from pydantic import SecretStr

    monkeypatch.setattr(meta_settings, "token_encryption_keys", SecretStr(""))
    with pytest.raises(AppError) as exc:
        InstagramOAuthService(db).start(human)
    assert exc.value.code == "token_encryption_not_configured" and exc.value.status_code == 503
    assert db.scalars(select(OAuthState)).first() is None  # nothing started


def test_viewer_and_agents_cannot_connect(db, viewer, agent, meta_settings):
    with pytest.raises(PermissionDeniedError):
        InstagramOAuthService(db).start(viewer)
    with pytest.raises(PermissionDeniedError):
        InstagramOAuthService(db).start(agent)


# ------------------------------------------------------------------ callback
@respx.mock
def test_full_connect_flow(db, human, user, meta_settings):
    token_route, exchange_route, me_route = mock_meta()
    state = start_state(db, human)
    result = InstagramOAuthService(db).complete(human, state=state, code="AQBcode123#_")
    # code exchange: documented form fields, '#_' stripped
    sent = parse_qs(token_route.calls.last.request.content.decode())
    assert sent["code"] == ["AQBcode123"] and sent["grant_type"] == ["authorization_code"]
    assert sent["client_secret"] == [FAKE_APP_SECRET]
    ex = exchange_route.calls.last.request.url.params
    assert ex["grant_type"] == "ig_exchange_token" and ex["access_token"] == SHORT
    assert me_route.calls.last.request.url.params["access_token"] == LONG

    account = result.account
    assert account.ig_user_id == IG_ID and account.ig_app_scoped_id == "app-scoped-9"
    assert account.username == "muxriddin.design"
    assert account.account_type == InstagramAccountType.BUSINESS
    assert account.user_id == user.id
    token = db.scalars(select(OAuthToken)).one()
    assert LONG not in token.token_ciphertext and SHORT not in token.token_ciphertext
    assert TokenCipher.from_settings().decrypt(token.token_ciphertext) == LONG
    assert token.expires_at > utcnow() + timedelta(days=59)
    assert "instagram_business_content_publish" in token.scopes
    assert result.warnings == []
    # Nothing secret in the audit log
    for row in db.scalars(select(AuditLog)):
        text = json.dumps(row.details) + (row.error or "")
        for secret in (SHORT, LONG, FAKE_APP_SECRET, "AQBcode123"):
            assert secret not in text


@respx.mock
def test_flat_response_and_creator_warning(db, human, meta_settings):
    mock_meta(flat=True, account_type="MEDIA_CREATOR")
    result = InstagramOAuthService(db).complete(human, state=start_state(db, human), code="c")
    assert result.account.account_type == InstagramAccountType.CREATOR
    assert any("Stories" in w for w in result.warnings)


@respx.mock
def test_missing_required_permission(db, human, meta_settings):
    mock_meta(perms="instagram_business_basic")
    with pytest.raises(AppError) as exc:
        InstagramOAuthService(db).complete(human, state=start_state(db, human), code="c")
    assert exc.value.code == "instagram_permission_missing"
    assert db.scalars(select(OAuthToken)).all() == []
    assert db.scalars(select(AuditLog).where(AuditLog.action == "INSTAGRAM_OAUTH_FAILED")).one()


@respx.mock
def test_long_lived_exchange_failure_saves_nothing(db, human, meta_settings):
    mock_meta(long_status=400)
    with pytest.raises(MetaApiError) as exc:
        InstagramOAuthService(db).complete(human, state=start_state(db, human), code="c")
    assert exc.value.kind == MetaErrorKind.TOKEN_EXPIRED
    assert exc.value.details["fbtrace_id"] == "TRACE1"
    assert db.scalars(select(InstagramAccount)).all() == []
    assert db.scalars(select(OAuthToken)).all() == []


def test_user_denied(db, human, meta_settings):
    with pytest.raises(AppError) as exc:
        InstagramOAuthService(db).complete(
            human,
            state=start_state(db, human),
            code=None,
            error="access_denied",
            error_description="The user denied your request.",
        )
    assert exc.value.code == "instagram_oauth_denied"


@pytest.mark.parametrize("case", ["unknown", "reused", "expired", "other_user"])
@respx.mock
def test_state_validation(db, human, meta_settings, case):
    from app.core.actors import HumanActor
    from app.core.security import hash_password
    from app.models import User
    from app.models.enums import UserRole

    mock_meta()
    state = start_state(db, human)
    actor = human
    if case == "unknown":
        state = "x" * 43
    elif case == "reused":
        InstagramOAuthService(db).complete(human, state=state, code="c")
    elif case == "expired":
        db.execute(update(OAuthState).values(expires_at=utcnow() - timedelta(seconds=1)))
        db.commit()
    elif case == "other_user":
        other = User(
            email="other@example.com", password_hash=hash_password("x" * 12), role=UserRole.ADMIN
        )
        db.add(other)
        db.commit()
        actor = HumanActor(user_id=other.id)
    with pytest.raises(AppError) as exc:
        InstagramOAuthService(db).complete(actor, state=state, code="c")
    assert exc.value.code == "instagram_oauth_state_invalid"
    if case == "other_user":  # a stolen state is burned and cannot be used by its owner either
        with pytest.raises(AppError):
            InstagramOAuthService(db).complete(human, state=state, code="c")


# ------------------------------------------------------------------ refresh
@respx.mock
def test_refresh_rules_and_success(db, human, meta_settings):
    mock_meta()
    account = (
        InstagramOAuthService(db).complete(human, state=start_state(db, human), code="c").account
    )
    with pytest.raises(AppError) as exc:
        InstagramOAuthService(db).refresh_account(account.id, human)
    assert exc.value.code == "instagram_refresh_too_early"  # Meta: >= 24 h old
    db.execute(
        update(OAuthToken).values(
            last_refreshed_at=utcnow() - timedelta(days=50),
            expires_at=utcnow() + timedelta(days=10),
        )
    )
    db.commit()
    route = respx.get(f"{META['graph']}/refresh_access_token").mock(
        return_value=httpx.Response(
            200, json={"access_token": LONG2, "token_type": "bearer", "expires_in": 5184000}
        )
    )
    result = InstagramOAuthService(db).refresh_due()
    assert result["refreshed"] == 1
    assert route.calls.last.request.url.params["grant_type"] == "ig_refresh_token"
    active = db.scalars(select(OAuthToken).where(OAuthToken.revoked_at.is_(None))).one()
    assert TokenCipher.from_settings().decrypt(active.token_ciphertext) == LONG2
    assert len(db.scalars(select(OAuthToken)).all()) == 2  # old one revoked, kept for audit
    assert db.scalars(select(AuditLog).where(AuditLog.action == "OAUTH_TOKEN_REFRESHED")).one()
    assert InstagramOAuthService(db).refresh_due()["refreshed"] == 0  # not due anymore


@respx.mock
def test_refresh_failure_and_expired(db, human, meta_settings):
    mock_meta()
    account = (
        InstagramOAuthService(db).complete(human, state=start_state(db, human), code="c").account
    )
    db.execute(
        update(OAuthToken).values(
            last_refreshed_at=utcnow() - timedelta(days=50), expires_at=utcnow() + timedelta(days=3)
        )
    )
    db.commit()
    respx.get(f"{META['graph']}/refresh_access_token").mock(
        return_value=httpx.Response(
            400,
            json={
                "error": {
                    "message": "Session has expired",
                    "type": "OAuthException",
                    "code": 190,
                    "error_subcode": 463,
                }
            },
        )
    )
    assert InstagramOAuthService(db).refresh_due()["failed"] == 1
    assert db.scalars(select(AuditLog).where(AuditLog.action == "OAUTH_TOKEN_REFRESH_FAILED")).one()
    db.execute(update(OAuthToken).values(expires_at=utcnow() - timedelta(minutes=1)))
    db.commit()
    with pytest.raises(MetaApiError) as exc:
        InstagramOAuthService(db).refresh_account(account.id, SystemActor("x"))
    assert exc.value.kind == MetaErrorKind.TOKEN_EXPIRED
    status = InstagramOAuthService(db).statuses()[0]
    assert status.needs_reconnect


# ------------------------------------------------------------------ status / disconnect
@respx.mock
def test_readiness_sees_connected_account_and_disconnect(db, human, meta_settings):
    mock_meta()
    account = (
        InstagramOAuthService(db).complete(human, state=start_state(db, human), code="c").account
    )
    content = make_ready(db, human)
    checks = {c.key: c.ok for c in ReviewService(db).readiness(content.id).checks}
    assert checks["instagram_account"]
    InstagramOAuthService(db).disconnect(account.id, human)
    checks = {c.key: c.ok for c in ReviewService(db).readiness(content.id).checks}
    assert not checks["instagram_account"]
    assert InstagramOAuthService(db).statuses() == []


# ------------------------------------------------------------------ Meta callbacks
def signed(payload: dict, secret: str = FAKE_APP_SECRET) -> str:
    body = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip("=")
    sig = hmac.new(secret.encode(), body.encode(), hashlib.sha256).digest()
    return base64.urlsafe_b64encode(sig).decode().rstrip("=") + "." + body


@respx.mock
def test_deauthorize_and_data_deletion(db, human, meta_settings):
    mock_meta()
    account = (
        InstagramOAuthService(db).complete(human, state=start_state(db, human), code="c").account
    )
    db.add(
        AnalyticsSnapshot(
            instagram_account_id=account.id,
            scope="account",
            captured_at=utcnow(),
            metrics={"reach": 1},
        )
    )
    db.commit()
    service = InstagramOAuthService(db)
    assert service.deauthorize(signed({"algorithm": "HMAC-SHA256", "user_id": "app-scoped-9"})) == 1
    assert db.scalars(select(OAuthToken).where(OAuthToken.revoked_at.is_(None))).all() == []
    record = service.data_deletion(signed({"algorithm": "HMAC-SHA256", "user_id": IG_ID}))
    assert db.scalars(select(OAuthToken)).all() == []  # ciphertext deleted
    assert db.scalars(select(AnalyticsSnapshot)).all() == []
    db.refresh(account)
    assert account.username is None and account.deleted_at is not None
    assert service.deletion_status(record.confirmation_code).status == "completed"
    assert db.scalars(select(DataDeletionRequest)).one().platform_user_id == IG_ID


@pytest.mark.parametrize(
    "bad",
    [
        lambda: signed({"algorithm": "HMAC-SHA256", "user_id": "1"}, secret="wrong"),
        lambda: signed({"algorithm": "MD5", "user_id": "1"}),
        lambda: signed({"algorithm": "HMAC-SHA256"}),
        lambda: "not-a-signed-request",
    ],
)
def test_signed_request_rejected(db, meta_settings, bad):
    with pytest.raises(AppError) as exc:
        InstagramOAuthService(db).deauthorize(bad())
    assert exc.value.code == "invalid_signed_request"


# ------------------------------------------------------------------ errors / safety
@pytest.mark.parametrize(
    ("code", "sub", "kind"),
    [
        (190, 463, MetaErrorKind.TOKEN_EXPIRED),
        (4, None, MetaErrorKind.RATE_LIMIT),
        (10, None, MetaErrorKind.PERMISSION_DENIED),
        (200, None, MetaErrorKind.PERMISSION_DENIED),
        (2, None, MetaErrorKind.TRANSIENT),
        (100, None, MetaErrorKind.INVALID_REQUEST),
        (36003, None, MetaErrorKind.MEDIA_VALIDATION),
        (999, None, MetaErrorKind.UNKNOWN),
    ],
)
def test_error_classification(code, sub, kind):
    assert classify(code, sub, None) == kind
    err = from_response(400, {"error": {"code": code, "error_subcode": sub, "message": "m"}})
    assert err.kind == kind and err.code == f"meta_{kind.value}"


def test_oauth_host_error_shape():
    err = from_response(
        400, {"error_type": "OAuthException", "code": 400, "error_message": "Invalid code"}
    )
    assert err.kind == MetaErrorKind.OAUTH and "Instagram" in err.message


def test_strip_code():
    assert strip_code("abc#_") == "abc" and strip_code(" abc ") == "abc"


@respx.mock
def test_network_errors_and_no_token_in_logs(db, human, meta_settings, caplog):
    from app.core.logging import configure_logging

    configure_logging("INFO", json_output=False)
    caplog.set_level(logging.DEBUG)
    respx.post(META["token"]).mock(side_effect=httpx.ConnectError("dns"))
    with pytest.raises(MetaApiError) as exc:
        InstagramOAuthService(db).complete(human, state=start_state(db, human), code="SECRETCODE")
    assert exc.value.kind == MetaErrorKind.NETWORK and exc.value.status_code == 503
    mock_meta()
    InstagramOAuthService(db).complete(human, state=start_state(db, human), code="c")
    for secret in (SHORT, LONG, FAKE_APP_SECRET, "SECRETCODE"):
        assert secret not in caplog.text


# ------------------------------------------------------------------ API
@pytest.fixture
def api(client, auth_headers):
    client.headers.update(auth_headers)
    return client


@respx.mock
def test_api_flow(api, meta_settings):
    status = api.get("/api/v1/instagram/status").json()
    assert status["configured"] is True and status["accounts"] == []
    assert FAKE_APP_SECRET not in json.dumps(status)
    url = api.post("/api/v1/instagram/oauth/start").json()["authorize_url"]
    state = parse_qs(urlparse(url).query)["state"][0]
    mock_meta()
    r = api.post("/api/v1/instagram/oauth/callback", json={"state": state, "code": "abc#_"})
    assert r.status_code == 200, r.text
    account = r.json()["account"]
    assert account["username"] == "muxriddin.design" and account["needs_reconnect"] is False
    assert LONG not in r.text
    again = api.post("/api/v1/instagram/oauth/callback", json={"state": state, "code": "abc"})
    assert again.status_code == 400
    assert api.delete(f"/api/v1/instagram/accounts/{account['id']}").status_code == 204


def test_api_not_configured(api):
    r = api.post("/api/v1/instagram/oauth/start")
    assert r.status_code == 503 and r.json()["error"]["code"] == "meta_not_configured"


def test_api_meta_callbacks_public_but_signed(client, meta_settings):
    r = client.post("/api/v1/instagram/meta/deauthorize", data={"signed_request": "bad.bad"})
    assert r.status_code == 400
    r = client.post(
        "/api/v1/instagram/meta/data-deletion",
        data={"signed_request": signed({"algorithm": "HMAC-SHA256", "user_id": "9"})},
    )
    assert r.status_code == 200
    code = r.json()["confirmation_code"]
    assert code in r.json()["url"]
    assert (
        client.get(f"/api/v1/instagram/meta/data-deletion/{code}").json()["status"] == "completed"
    )


@pytest.mark.parametrize(
    ("method", "path"),
    [
        ("get", "/api/v1/instagram/status"),
        ("post", "/api/v1/instagram/oauth/start"),
        ("post", "/api/v1/instagram/oauth/callback"),
        ("delete", "/api/v1/instagram/accounts/1"),
        ("post", "/api/v1/instagram/accounts/1/refresh-token"),
    ],
)
def test_api_requires_auth(client, method, path):
    assert getattr(client, method)(path).status_code == 401
