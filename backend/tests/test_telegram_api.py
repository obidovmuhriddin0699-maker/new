import pytest
from sqlalchemy import select

from app.models import TelegramLinkCode
from app.services.telegram import TelegramService
from tests.conftest import TG_OWNER


@pytest.fixture
def api(client, auth_headers):
    client.headers.update(auth_headers)
    return client


def test_status_not_linked(api, tg_settings):
    data = api.get("/api/v1/telegram/status").json()
    assert data["enabled"] is False and data["linked"] is False
    assert "/approve" in data["commands"]
    assert "token" not in str(data).lower()


def test_link_code_and_unlink(api, db, user, tg_settings, monkeypatch):
    monkeypatch.setattr(tg_settings, "telegram_bot_username", "muxriddin_bot")
    r = api.post("/api/v1/telegram/link-code")
    assert r.status_code == 201
    body = r.json()
    assert body["deep_link"] == f"https://t.me/muxriddin_bot?start={body['code'].replace('-', '')}"
    assert db.scalars(select(TelegramLinkCode)).one().code_hash != body["code"]
    TelegramService(db).link(TG_OWNER, body["code"])
    status = api.get("/api/v1/telegram/status").json()
    assert status["linked"] is True and status["allowed"] is True
    assert api.delete("/api/v1/telegram/link").status_code == 204
    assert api.get("/api/v1/telegram/status").json()["linked"] is False


def test_requires_auth(client):
    assert client.get("/api/v1/telegram/status").status_code == 401
    assert client.post("/api/v1/telegram/link-code").status_code == 401
    assert client.delete("/api/v1/telegram/link").status_code == 401


def test_production_requires_token_and_allowlist(monkeypatch):
    from pydantic import ValidationError

    from app.core.config import Settings

    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("JWT_SECRET_KEY", "x" * 48)
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://u:p@db/x")
    monkeypatch.setenv("CORS_ORIGINS", "https://panel.example.com")
    monkeypatch.setenv("TELEGRAM_ENABLED", "true")
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "")
    with pytest.raises(ValidationError, match="TELEGRAM_ENABLED requires"):
        Settings(_env_file=None)


def test_allowlist_parsing(monkeypatch):
    from app.core.config import Settings

    monkeypatch.setenv("TELEGRAM_ALLOWED_USER_IDS", "111, 222;333")
    assert Settings(_env_file=None).telegram_allowed_user_ids == [111, 222, 333]
