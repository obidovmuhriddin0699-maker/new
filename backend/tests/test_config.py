import pytest
from pydantic import ValidationError

from app.core.config import Settings, get_settings


def test_settings_load_from_env():
    s = get_settings()
    assert s.app_env == "test"
    assert s.ai_model == "qwen2.5:3b"
    assert s.meta_login_mode == "instagram"
    assert s.meta_dry_run is True


def test_sqlite_fallback_when_database_url_empty(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "")
    s = Settings(_env_file=None)
    assert s.effective_database_url.startswith("sqlite:///")
    assert s.is_sqlite


def test_cors_origins_comma_separated(monkeypatch):
    monkeypatch.setenv("CORS_ORIGINS", "http://a.test, http://b.test")
    assert Settings(_env_file=None).cors_origins == ["http://a.test", "http://b.test"]


def test_ai_model_is_configurable(monkeypatch):
    monkeypatch.setenv("AI_MODEL", "llama3.2:3b")
    assert Settings(_env_file=None).ai_model == "llama3.2:3b"


def test_production_rejects_insecure_defaults(monkeypatch):
    for key in ("JWT_SECRET_KEY", "TOKEN_ENCRYPTION_KEYS", "DATABASE_URL"):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv("APP_ENV", "production")
    with pytest.raises(ValidationError) as exc:
        Settings(_env_file=None)
    msg = str(exc.value)
    assert "JWT_SECRET_KEY" in msg
    assert "TOKEN_ENCRYPTION_KEYS" in msg
    assert "DATABASE_URL" in msg


def test_production_accepts_proper_config(monkeypatch):
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("JWT_SECRET_KEY", "x" * 48)
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://u:p@db/x")
    monkeypatch.setenv("CORS_ORIGINS", "https://panel.example.com")
    monkeypatch.setenv("RATE_LIMIT_BACKEND", "auto")  # tests default to memory
    monkeypatch.setenv("ALLOWED_HOSTS", "panel.example.com,backend")
    monkeypatch.setenv("PANEL_PUBLIC_URL", "https://panel.example.com")
    s = Settings(_env_file=None)
    assert s.app_env == "production"


@pytest.mark.parametrize(
    ("env", "message"),
    [
        ({"ALLOWED_HOSTS": ""}, "ALLOWED_HOSTS"),
        ({"PANEL_PUBLIC_URL": "http://panel.example.com"}, "PANEL_PUBLIC_URL"),
        ({"TRUSTED_PROXIES": "10.0.0.0/8,0.0.0.0/0"}, "TRUSTED_PROXIES"),
        ({"JWT_ALGORITHM": "none"}, "JWT_ALGORITHM"),
    ],
)
def test_production_rejects_unsafe_edges(monkeypatch, env, message):
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("JWT_SECRET_KEY", "x" * 48)
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://u:p@db/x")
    monkeypatch.setenv("CORS_ORIGINS", "https://panel.example.com")
    monkeypatch.setenv("RATE_LIMIT_BACKEND", "auto")
    monkeypatch.setenv("ALLOWED_HOSTS", "panel.example.com")
    monkeypatch.setenv("PANEL_PUBLIC_URL", "https://panel.example.com")
    for key, value in env.items():
        monkeypatch.setenv(key, value)
    with pytest.raises(ValueError, match=message):
        Settings(_env_file=None)


def test_production_requires_shared_rate_limiting(monkeypatch):
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("JWT_SECRET_KEY", "x" * 48)
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://u:p@db/x")
    monkeypatch.setenv("CORS_ORIGINS", "https://panel.example.com")
    monkeypatch.setenv("RATE_LIMIT_BACKEND", "memory")
    with pytest.raises(ValueError, match="Rate limiting"):
        Settings(_env_file=None)


def test_secrets_are_masked_in_repr():
    s = get_settings()
    text = repr(s)
    assert s.jwt_secret_key.get_secret_value() not in text
    assert s.token_encryption_keys.get_secret_value() not in text


@pytest.mark.parametrize(
    "url",
    [
        "postgres://u:p@db.railway.internal:5432/railway",
        "postgresql://u:p@db.railway.internal:5432/railway",
    ],
)
def test_platform_postgres_urls_use_the_psycopg3_driver(url):
    from app.core.config import Settings

    settings = Settings(database_url=url)
    assert settings.database_url == "postgresql+psycopg://u:p@db.railway.internal:5432/railway"
    assert (
        Settings(database_url="postgresql+psycopg://x@h/d").database_url
        == "postgresql+psycopg://x@h/d"
    )
