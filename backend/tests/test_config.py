import pytest

from backend.app.config import (
    LOCAL_CORS_ORIGINS,
    cookie_secure,
    cors_origins,
    is_production,
    validate_production_configuration,
)
from backend.app.database import normalize_database_url


def production_environment(**overrides: str) -> dict[str, str]:
    environment = {
        "APP_ENV": "production",
        "COOKIE_SECURE": "true",
        "OLLAMA_BASE_URL": "https://ollama.example.net",
    }
    environment.update(overrides)
    return environment


def test_railway_production_cannot_be_overridden_by_development_label() -> None:
    assert is_production(
        {
            "APP_ENV": "development",
            "RAILWAY_ENVIRONMENT": "production",
        }
    )


def test_secure_cookies_default_on_in_production_and_off_locally() -> None:
    assert cookie_secure({"RAILWAY_ENVIRONMENT": "production"})
    assert not cookie_secure({})
    assert not cookie_secure({"APP_ENV": "development", "COOKIE_SECURE": "false"})


def test_cookie_secure_rejects_invalid_values() -> None:
    with pytest.raises(RuntimeError, match="COOKIE_SECURE"):
        cookie_secure({"COOKIE_SECURE": "sometimes"})


def test_cors_defaults_to_local_origins_only_outside_production() -> None:
    assert cors_origins({}) == list(LOCAL_CORS_ORIGINS)
    assert cors_origins({"RAILWAY_ENVIRONMENT": "production"}) == []


@pytest.mark.parametrize(
    "origins",
    ["*", "https://frontend.example/path", "http://frontend.example"],
)
def test_production_cors_rejects_wildcards_paths_and_http(origins: str) -> None:
    with pytest.raises(RuntimeError, match="CORS_ORIGINS"):
        cors_origins(
            {
                "APP_ENV": "production",
                "CORS_ORIGINS": origins,
            }
        )


def test_production_configuration_accepts_postgres_secure_cookies_and_remote_ollama() -> None:
    validate_production_configuration(
        production_environment(CORS_ORIGINS="https://panel.example.net"),
        "postgresql+psycopg",
    )


@pytest.mark.parametrize(
    ("environment", "database_driver", "message"),
    [
        (production_environment(), "sqlite", "PostgreSQL"),
        (
            production_environment(COOKIE_SECURE="false"),
            "postgresql+psycopg",
            "COOKIE_SECURE",
        ),
        (
            production_environment(OLLAMA_BASE_URL="http://127.0.0.1:11434"),
            "postgresql+psycopg",
            "localhost",
        ),
        (
            production_environment(OLLAMA_BASE_URL=""),
            "postgresql+psycopg",
            "OLLAMA_BASE_URL",
        ),
    ],
)
def test_production_configuration_rejects_unsafe_or_ephemeral_settings(
    environment: dict[str, str],
    database_driver: str,
    message: str,
) -> None:
    with pytest.raises(RuntimeError, match=message):
        validate_production_configuration(environment, database_driver)


@pytest.mark.parametrize(
    ("url", "expected"),
    [
        (
            "postgres://user:password@db.example/app",
            "postgresql+psycopg://user:password@db.example/app",
        ),
        (
            "postgresql://user:password@db.example/app",
            "postgresql+psycopg://user:password@db.example/app",
        ),
        ("sqlite:///./app.db", "sqlite:///./app.db"),
    ],
)
def test_database_url_normalizes_railway_postgres_schemes(url: str, expected: str) -> None:
    assert normalize_database_url(url) == expected
