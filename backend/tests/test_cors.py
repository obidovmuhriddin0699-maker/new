from fastapi.testclient import TestClient

from backend.app.main import create_app


def test_frontend_preflight_allows_credentials_csrf_and_json(test_engine) -> None:
    with TestClient(create_app(test_engine)) as client:
        response = client.options(
            "/auth/login",
            headers={
                "Origin": "http://127.0.0.1:5173",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "content-type,x-csrf-token",
            },
        )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://127.0.0.1:5173"
    assert response.headers["access-control-allow-credentials"] == "true"
    assert "x-csrf-token" in response.headers["access-control-allow-headers"].lower()


def test_unconfigured_origin_is_not_granted_cors_access(test_engine) -> None:
    with TestClient(create_app(test_engine)) as client:
        response = client.options(
            "/auth/login",
            headers={
                "Origin": "https://untrusted.example",
                "Access-Control-Request-Method": "POST",
            },
        )

    assert response.headers.get("access-control-allow-origin") is None


def test_frontend_preflight_allows_account_unlink(test_engine) -> None:
    with TestClient(create_app(test_engine)) as client:
        response = client.options(
            "/telegram/link",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "DELETE",
                "Access-Control-Request-Headers": "x-csrf-token",
            },
        )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"
    assert "delete" in response.headers["access-control-allow-methods"].lower()
