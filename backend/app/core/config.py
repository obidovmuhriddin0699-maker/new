"""Application configuration.

All settings come from environment variables (or a local ``.env`` file).
Nothing secret is hard-coded here: secret fields have no production default and
are validated at startup when ``APP_ENV=production``.
"""

from functools import lru_cache
from typing import Annotated, Literal

from pydantic import Field, SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict

Environment = Literal["development", "test", "production"]

# Placeholder used only for local development. Production refuses to start with it.
_DEV_JWT_SECRET = "dev-only-insecure-jwt-secret-change-me"  # noqa: S105


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # --- App ---
    app_name: str = "MUXRIDDIN AI INSTAGRAM MANAGER"
    app_env: Environment = "development"
    debug: bool = False
    log_level: str = "INFO"
    log_json: bool = True
    api_v1_prefix: str = "/api/v1"

    # --- CORS ---
    cors_origins: Annotated[list[str], NoDecode] = Field(
        default_factory=lambda: ["http://localhost:3000"]
    )

    # --- Database ---
    # Empty -> SQLite fallback for local development.
    database_url: str = ""
    sqlite_path: str = "./data/muxriddin.db"
    db_echo: bool = False

    # --- Redis / Celery ---
    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = ""
    celery_result_backend: str = ""
    celery_task_always_eager: bool = False

    # --- Auth ---
    jwt_secret_key: SecretStr = SecretStr(_DEV_JWT_SECRET)
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # --- Token encryption (Fernet). Comma-separated: first key encrypts, all keys decrypt.
    token_encryption_keys: SecretStr = SecretStr("")

    # --- AI provider ---
    # "mock" is deterministic and for tests/demos only; refused in production.
    ai_provider: Literal["ollama", "mock"] = "ollama"
    ollama_base_url: str = "http://localhost:11434"
    ai_model: str = "qwen2.5:3b"
    ai_timeout_seconds: float = 120.0
    ai_temperature: float = 0.6
    ai_max_output_tokens: int = 2048
    ai_max_response_chars: int = 60_000
    ai_structured_max_attempts: int = 2  # 1 call + 1 repair attempt for invalid JSON
    # "sync": run generation inside the request (dev default).
    # "celery": enqueue an AIJob for the worker and return 202 immediately.
    ai_jobs_mode: Literal["sync", "celery"] = "sync"
    ai_max_active_jobs_per_user: int = 3

    # --- Media generation (no real provider in PHASE 3) ---
    image_provider: Literal["none", "mock"] = "none"
    video_provider: Literal["none", "mock"] = "none"

    # --- Telegram bot (PHASE 5) ---
    telegram_enabled: bool = False
    telegram_bot_token: SecretStr = SecretStr("")
    telegram_bot_username: str = ""  # without @, used for deep links in the panel
    # Telegram user IDs allowed to talk to the bot (in addition to account linking).
    telegram_allowed_user_ids: Annotated[list[int], NoDecode] = Field(default_factory=list)
    telegram_action_ttl_hours: int = 72
    telegram_link_code_ttl_minutes: int = 10
    telegram_notify_interval_seconds: int = 15
    panel_public_url: str = "http://localhost:3000"

    # --- Meta / Instagram (PHASE 7+). Only non-secret config here in PHASE 1.
    meta_login_mode: Literal["instagram", "facebook"] = "instagram"
    meta_graph_api_version: str = "v26.0"
    meta_dry_run: bool = True

    @field_validator("cors_origins", mode="before")
    @classmethod
    def _split_origins(cls, value: object) -> object:
        if isinstance(value, str):
            value = value.strip()
            if value.startswith("["):
                import json

                return json.loads(value)
            return [o.strip() for o in value.split(",") if o.strip()]
        return value

    @field_validator("telegram_allowed_user_ids", mode="before")
    @classmethod
    def _split_ids(cls, value: object) -> object:
        if isinstance(value, str):
            return [int(v) for v in value.replace(";", ",").split(",") if v.strip()]
        if isinstance(value, int):
            return [value]
        return value

    @model_validator(mode="after")
    def _check_production(self) -> "Settings":
        if self.app_env == "production":
            problems = []
            secret = self.jwt_secret_key.get_secret_value()
            if secret == _DEV_JWT_SECRET or len(secret) < 32:
                problems.append("JWT_SECRET_KEY must be set (>= 32 chars)")
            if not self.token_encryption_keys.get_secret_value():
                problems.append("TOKEN_ENCRYPTION_KEYS must be set")
            if not self.database_url.startswith("postgresql"):
                problems.append("DATABASE_URL must point to PostgreSQL in production")
            if "*" in self.cors_origins:
                problems.append("CORS_ORIGINS must not contain '*' in production")
            if self.debug:
                problems.append("DEBUG must be false in production")
            if self.ai_provider == "mock":
                problems.append("AI_PROVIDER=mock is not allowed in production")
            if self.telegram_enabled and (
                not self.telegram_bot_token.get_secret_value() or not self.telegram_allowed_user_ids
            ):
                problems.append(
                    "TELEGRAM_ENABLED requires TELEGRAM_BOT_TOKEN and TELEGRAM_ALLOWED_USER_IDS"
                )
            if "mock" in (self.image_provider, self.video_provider):
                problems.append("mock media providers are not allowed in production")
            if problems:
                raise ValueError("Invalid production configuration: " + "; ".join(problems))
        return self

    @property
    def effective_database_url(self) -> str:
        return self.database_url or f"sqlite:///{self.sqlite_path}"

    @property
    def is_sqlite(self) -> bool:
        return self.effective_database_url.startswith("sqlite")

    @property
    def effective_celery_broker_url(self) -> str:
        return self.celery_broker_url or self.redis_url

    @property
    def effective_celery_result_backend(self) -> str:
        return self.celery_result_backend or self.redis_url


@lru_cache
def get_settings() -> Settings:
    return Settings()
