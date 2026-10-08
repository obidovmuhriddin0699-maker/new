from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import event
from sqlalchemy.exc import OperationalError

from backend.app.main import create_app


def test_root_and_health(client) -> None:
    assert client.get("/").json() == {"message": "Local AI SaaS API"}
    assert client.get("/health").json() == {"status": "ok"}
    assert client.get("/ready").json() == {"status": "ready"}


def test_root_serves_frontend_bundle_when_present(test_engine, tmp_path: Path) -> None:
    assets = tmp_path / "assets"
    assets.mkdir()
    (assets / "app.js").write_text("ok", encoding="utf-8")
    (tmp_path / "index.html").write_text("<html>panel</html>", encoding="utf-8")

    with TestClient(create_app(test_engine, tmp_path)) as client:
        response = client.get("/")
        asset_response = client.get("/assets/app.js")

    assert response.status_code == 200
    assert response.text == "<html>panel</html>"
    assert asset_response.text == "ok"


def test_liveness_remains_ok_when_database_readiness_fails(test_engine) -> None:
    def fail_select_one(connection, cursor, statement, parameters, context, executemany):
        if statement == "SELECT 1":
            raise OperationalError(statement, parameters, RuntimeError("database offline"))

    with TestClient(create_app(test_engine)) as client:
        event.listen(test_engine, "before_cursor_execute", fail_select_one)
        try:
            assert client.get("/health").status_code == 200
            readiness = client.get("/ready")
        finally:
            event.remove(test_engine, "before_cursor_execute", fail_select_one)

    assert readiness.status_code == 503
    assert readiness.json()["detail"] == "Database is unavailable"
