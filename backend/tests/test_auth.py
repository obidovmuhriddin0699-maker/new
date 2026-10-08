import time

from fastapi import Response
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.dependencies import CSRF_COOKIE_NAME, SESSION_COOKIE_NAME
from backend.app.models import AuthSession, User
from backend.app.security import hash_token
from backend.app.routers.auth import set_session_cookies


def register(client: TestClient, email: str) -> dict:
    response = client.post(
        "/auth/register",
        json={"email": email, "password": "correct horse battery staple"},
    )
    assert response.status_code == 201
    return response.json()


def csrf_headers(client: TestClient) -> dict[str, str]:
    return {"X-CSRF-Token": client.cookies[CSRF_COOKIE_NAME]}


def test_register_hashes_password_sets_secure_session_cookies_and_me(client, test_engine) -> None:
    response = client.post(
        "/auth/register",
        json={"email": "  Alice@Example.com ", "password": "correct horse battery staple"},
    )

    assert response.status_code == 201
    assert response.json()["email"] == "alice@example.com"
    assert "password_hash" not in response.json()
    assert SESSION_COOKIE_NAME in client.cookies
    assert CSRF_COOKIE_NAME in client.cookies
    set_cookies = response.headers.get_list("set-cookie")
    session_cookie = next(cookie for cookie in set_cookies if cookie.startswith("session="))
    assert "httponly" in session_cookie.lower()
    assert "samesite=lax" in session_cookie.lower()

    with Session(test_engine) as db:
        user = db.scalar(select(User).where(User.email == "alice@example.com"))
        assert user is not None
        assert user.password_hash != "correct horse battery staple"
        session = db.scalar(
            select(AuthSession).where(
                AuthSession.token_hash == hash_token(client.cookies[SESSION_COOKIE_NAME])
            )
        )
        assert session is not None
        assert session.expires_at > int(time.time())

    current = client.get("/auth/me")
    assert current.status_code == 200
    assert current.json()["workspaces"] == []


def test_duplicate_registration_and_invalid_login_are_rejected(client) -> None:
    register(client, "user@example.com")
    duplicate = client.post(
        "/auth/register",
        json={"email": "USER@example.com", "password": "correct horse battery staple"},
    )
    invalid_login = client.post(
        "/auth/login",
        json={"email": "user@example.com", "password": "wrong password"},
    )

    assert duplicate.status_code == 409
    assert invalid_login.status_code == 401


def test_login_logout_and_expired_session_lifecycle(client, test_engine) -> None:
    register(client, "user@example.com")
    csrf = csrf_headers(client)
    assert client.post("/auth/logout", headers=csrf).status_code == 204
    assert client.get("/auth/me").status_code == 401

    response = client.post(
        "/auth/login",
        json={"email": "USER@example.com", "password": "correct horse battery staple"},
    )
    assert response.status_code == 200
    assert client.get("/auth/me").status_code == 200

    with Session(test_engine) as db:
        session = db.scalar(
            select(AuthSession).where(
                AuthSession.token_hash == hash_token(client.cookies[SESSION_COOKIE_NAME])
            )
        )
        assert session is not None
        session.expires_at = int(time.time()) - 1
        db.commit()

    assert client.get("/auth/me").status_code == 401


def test_auth_cookie_state_changes_require_csrf(client) -> None:
    register(client, "user@example.com")
    response = client.post("/workspaces", json={"name": "No CSRF"})
    logout = client.post("/auth/logout")

    assert response.status_code == 403
    assert logout.status_code == 403
    assert client.get("/auth/me").status_code == 200


def test_production_session_and_csrf_cookies_are_secure(monkeypatch) -> None:
    monkeypatch.setenv("RAILWAY_ENVIRONMENT", "production")
    monkeypatch.delenv("COOKIE_SECURE", raising=False)
    response = Response()

    set_session_cookies(response, "session-test", "csrf-test")

    cookies = response.headers.getlist("set-cookie")
    assert len(cookies) == 2
    assert all("secure" in cookie.lower() for cookie in cookies)
