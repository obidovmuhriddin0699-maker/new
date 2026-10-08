from app.core import database


def test_root_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert body["components"]["database"]["ok"] is True
    # Redis is unreachable in tests: reported, not fatal.
    assert body["components"]["redis"]["ok"] is False
    assert resp.headers["X-Request-ID"]


def test_versioned_health(client):
    assert client.get("/api/v1/health").status_code == 200


def test_health_degraded_when_db_down(client, monkeypatch):
    monkeypatch.setattr(database, "check_database", lambda: (False, "OperationalError"))
    from app.api import health as health_module

    monkeypatch.setattr(health_module, "check_database", lambda: (False, "OperationalError"))
    resp = client.get("/health")
    assert resp.status_code == 503
    assert resp.json()["status"] == "degraded"


def test_request_id_is_propagated(client):
    resp = client.get("/health", headers={"X-Request-ID": "abc123"})
    assert resp.headers["X-Request-ID"] == "abc123"


def test_health_does_not_leak_secrets(client):
    from app.core.config import get_settings

    s = get_settings()
    text = client.get("/health").text
    assert s.jwt_secret_key.get_secret_value() not in text
    assert s.token_encryption_keys.get_secret_value() not in text
    assert "sqlite" not in text and "postgres" not in text


def test_cors_allows_dev_frontend(client):
    resp = client.options(
        "/health",
        headers={"Origin": "http://localhost:3000", "Access-Control-Request-Method": "GET"},
    )
    assert resp.headers.get("access-control-allow-origin") == "http://localhost:3000"


def test_cors_rejects_unknown_origin(client):
    resp = client.get("/health", headers={"Origin": "https://evil.example"})
    assert "access-control-allow-origin" not in resp.headers


def test_openapi_available_in_dev(client):
    assert client.get("/openapi.json").status_code == 200
