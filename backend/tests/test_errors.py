from fastapi import APIRouter

from app.core.errors import NotFoundError


def test_404_shape(client):
    resp = client.get("/api/v1/does-not-exist")
    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "http_404"
    assert resp.json()["error"]["request_id"]


def test_validation_error_shape(client):
    resp = client.post("/api/v1/auth/login", json={"email": "not-an-email"})
    assert resp.status_code == 422
    err = resp.json()["error"]
    assert err["code"] == "validation_error"
    assert isinstance(err["details"], list)


def test_app_error_and_unhandled_error():
    from fastapi.testclient import TestClient

    from app.main import create_app

    app = create_app()
    router = APIRouter()

    @router.get("/boom")
    def boom():
        raise RuntimeError("database password is hunter2")

    @router.get("/missing")
    def missing():
        raise NotFoundError("Content not found")

    app.include_router(router)
    with TestClient(app, raise_server_exceptions=False) as c:
        resp = c.get("/boom")
        assert resp.status_code == 500
        assert resp.json()["error"] == {
            "code": "internal_error",
            "message": "Internal server error",
            "request_id": resp.headers["X-Request-ID"],
        }
        assert "hunter2" not in resp.text

        resp = c.get("/missing")
        assert resp.status_code == 404
        assert resp.json()["error"]["message"] == "Content not found"
