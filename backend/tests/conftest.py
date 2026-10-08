"""Test configuration.

Environment is set *before* the app is imported so no developer .env / real
service is ever used. Meta is always dry-run; there is no real network access.
"""

import os
import tempfile
from collections.abc import Iterator
from pathlib import Path

from cryptography.fernet import Fernet

_TMP = Path(tempfile.mkdtemp(prefix="muxriddin-tests-"))
os.environ.update(
    {
        "APP_ENV": "test",
        "DATABASE_URL": f"sqlite:///{_TMP / 'test.db'}",
        "REDIS_URL": "redis://127.0.0.1:1/0",  # deliberately unreachable
        "JWT_SECRET_KEY": "test-secret-key-that-is-long-enough-1234567890",
        "TOKEN_ENCRYPTION_KEYS": Fernet.generate_key().decode(),
        "OLLAMA_BASE_URL": "http://ollama.test:11434",
        "AI_MODEL": "qwen2.5:3b",
        "META_DRY_RUN": "true",
        "CELERY_TASK_ALWAYS_EAGER": "true",
        "LOG_JSON": "false",
    }
)

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy.orm import Session  # noqa: E402

from app.core.config import get_settings  # noqa: E402
from app.core.database import get_engine, get_sessionmaker, reset_engine  # noqa: E402
from app.core.security import hash_password  # noqa: E402
from app.models import Base, User  # noqa: E402

TEST_PASSWORD = "correct-horse-battery-staple"


@pytest.fixture(autouse=True)
def _fresh_db() -> Iterator[None]:
    get_settings.cache_clear()
    reset_engine()
    engine = get_engine()
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    yield
    reset_engine()


@pytest.fixture
def db() -> Iterator[Session]:
    with get_sessionmaker()() as session:
        yield session


@pytest.fixture
def client() -> Iterator[TestClient]:
    from app.main import create_app

    with TestClient(create_app()) as c:
        yield c


@pytest.fixture
def user(db: Session) -> User:
    u = User(email="owner@example.com", password_hash=hash_password(TEST_PASSWORD))
    db.add(u)
    db.commit()
    return u


@pytest.fixture
def auth_headers(client: TestClient, user: User) -> dict[str, str]:
    resp = client.post("/api/v1/auth/login", json={"email": user.email, "password": TEST_PASSWORD})
    assert resp.status_code == 200, resp.text
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}
