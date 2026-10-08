from datetime import UTC, datetime, timedelta

import jwt

from app.core.config import get_settings
from app.core.security import hash_password, verify_password
from tests.conftest import TEST_PASSWORD


def test_password_hash_is_argon2():
    h = hash_password("s3cret-password")
    assert h.startswith("$argon2")
    assert verify_password("s3cret-password", h)
    assert not verify_password("wrong", h)


def test_login_and_me(client, user, auth_headers):
    resp = client.get("/api/v1/auth/me", headers=auth_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["email"] == user.email
    assert "password_hash" not in body


def test_login_wrong_password(client, user):
    resp = client.post("/api/v1/auth/login", json={"email": user.email, "password": "nope"})
    assert resp.status_code == 401
    assert resp.json()["error"]["code"] == "authentication_failed"


def test_login_unknown_email_same_error(client, user):
    resp = client.post(
        "/api/v1/auth/login", json={"email": "ghost@example.com", "password": TEST_PASSWORD}
    )
    assert resp.status_code == 401
    assert resp.json()["error"]["message"] == "Invalid email or password"


def test_me_requires_token(client):
    assert client.get("/api/v1/auth/me").status_code == 401


def test_me_rejects_garbage_token(client):
    resp = client.get("/api/v1/auth/me", headers={"Authorization": "Bearer garbage"})
    assert resp.status_code == 401


def test_me_rejects_expired_token(client, user):
    s = get_settings()
    token = jwt.encode(
        {"sub": str(user.id), "type": "access", "exp": datetime.now(UTC) - timedelta(minutes=1)},
        s.jwt_secret_key.get_secret_value(),
        algorithm=s.jwt_algorithm,
    )
    resp = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 401
    assert resp.json()["error"]["code"] == "token_expired"


def test_token_signed_with_other_key_rejected(client, user):
    token = jwt.encode(
        {"sub": str(user.id), "type": "access", "exp": datetime.now(UTC) + timedelta(minutes=5)},
        "attacker-key-attacker-key-attacker-key",
        algorithm="HS256",
    )
    resp = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 401


def test_inactive_user_cannot_login(client, db, user):
    user.is_active = False
    db.commit()
    resp = client.post("/api/v1/auth/login", json={"email": user.email, "password": TEST_PASSWORD})
    assert resp.status_code == 401
