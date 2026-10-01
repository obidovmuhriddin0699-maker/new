import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine, create_engine
from sqlalchemy.pool import StaticPool

from backend.app.main import create_app


@pytest.fixture
def test_engine() -> Engine:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    try:
        yield engine
    finally:
        engine.dispose()


@pytest.fixture
def client(test_engine: Engine):
    app = create_app(test_engine)
    with TestClient(app) as test_client:
        yield test_client
