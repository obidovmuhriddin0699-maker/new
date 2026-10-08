import os
from collections.abc import Mapping
from urllib.parse import urlsplit


LOCAL_CORS_ORIGINS = (
    "http://localhost:5173",
    "http://127.0.0.1:5173",
)


def is_production(environment: Mapping[str, str] | None = None) -> bool:
    env = environment if environment is not None else os.environ
    values = (
        env.get("APP_ENV", ""),
        env.get("RAILWAY_ENVIRONMENT", ""),
        env.get("RAILWAY_ENVIRONMENT_NAME", ""),
    )
    return any(value.strip().lower() in {"production", "prod"} for value in values)


def cookie_secure(environment: Mapping[str, str] | None = None) -> bool:
    env = environment if environment is not None else os.environ
    configured = env.get("COOKIE_SECURE")
    if configured is None:
        return is_production(env)
    normalized = configured.strip().lower()
    if normalized not in {"true", "false"}:
        raise RuntimeError("COOKIE_SECURE must be either true or false")
    return normalized == "true"


def cors_origins(environment: Mapping[str, str] | None = None) -> list[str]:
    env = environment if environment is not None else os.environ
    configured = env.get("CORS_ORIGINS")
    if configured is None:
        return [] if is_production(env) else list(LOCAL_CORS_ORIGINS)

    origins = [origin.strip().rstrip("/") for origin in configured.split(",") if origin.strip()]
    for origin in origins:
        parsed = urlsplit(origin)
        if (
            origin == "*"
            or parsed.scheme not in {"http", "https"}
            or not parsed.netloc
            or parsed.path
            or parsed.query
            or parsed.fragment
            or parsed.username
            or parsed.password
        ):
            raise RuntimeError("CORS_ORIGINS must contain comma-separated origins, not URLs or wildcards")
        if is_production(env) and parsed.scheme != "https":
            raise RuntimeError("Production CORS_ORIGINS must use HTTPS")
    return origins


def validate_production_configuration(
    environment: Mapping[str, str],
    database_driver: str,
) -> None:
    if not is_production(environment):
        return
    if not database_driver.startswith("postgresql+psycopg"):
        raise RuntimeError("Production requires a persistent PostgreSQL DATABASE_URL")
    if not cookie_secure(environment):
        raise RuntimeError("COOKIE_SECURE must be true in production")
    cors_origins(environment)

    ollama_base_url = environment.get("OLLAMA_BASE_URL", "").strip()
    parsed_ollama = urlsplit(ollama_base_url)
    if parsed_ollama.scheme not in {"http", "https"} or not parsed_ollama.hostname:
        raise RuntimeError("Production requires an externally reachable OLLAMA_BASE_URL")
    if parsed_ollama.hostname.lower() in {
        "localhost",
        "127.0.0.1",
        "0.0.0.0",
        "::1",
    }:
        raise RuntimeError("Production OLLAMA_BASE_URL cannot point to localhost")
