import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select

from app.api.v1.ai import get_provider_factory
from app.models import ContentAsset
from app.providers.ai.base import AIProviderUnavailableError
from tests.conftest import TEST_PASSWORD, mock_factory

AI = "/api/v1/ai"


@pytest.fixture
def make_client(user):
    from app.main import create_app

    def _make(factory=None):
        app = create_app()
        app.dependency_overrides[get_provider_factory] = lambda: factory or mock_factory()
        return TestClient(app)

    return _make


@pytest.fixture
def api(make_client, brand):
    with make_client() as c:
        token = c.post(
            "/api/v1/auth/login", json={"email": "owner@example.com", "password": TEST_PASSWORD}
        ).json()
        c.headers["Authorization"] = f"Bearer {token['access_token']}"
        yield c


GEN = [
    ("/strategy", {}),
    ("/ideas", {"count": 2}),
    ("/content-plan", {"start_date": "2026-10-12"}),
    ("/generate-caption", {"topic": "Minimalizm"}),
    ("/generate-carousel", {"topic": "Minimalizm", "slides": 3}),
    ("/generate-reels-script", {"topic": "Minimalizm"}),
    ("/generate-story", {"topic": "Minimalizm"}),
    ("/hashtags", {"topic": "Minimalizm"}),
]


@pytest.mark.parametrize(("path", "body"), GEN)
def test_generation_endpoints_succeed(api, path, body):
    r = api.post(AI + path, json=body)
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["job"]["status"] == "SUCCEEDED" and data["result"]
    if data["content_id"]:
        assert data["content_status"] in ("DRAFT", "READY_FOR_REVIEW")
        content = api.get(f"/api/v1/contents/{data['content_id']}").json()
        assert content["status"] != "APPROVED" and content["publish_authorized"] is False


@pytest.mark.parametrize(
    ("path", "body"),
    GEN + [("/evaluate-content", {"content_type": "POST"}), ("/generate-image", {"content_id": 1})],
)
def test_endpoints_require_auth(make_client, path, body):
    with make_client() as c:
        assert c.post(AI + path, json=body).status_code == 401
    with make_client() as c:
        assert c.get(AI + "/status").status_code == 401
        assert c.get(AI + "/jobs/1").status_code == 401


def test_viewer_cannot_generate(make_client, brand, viewer):
    with make_client() as c:
        token = c.post(
            "/api/v1/auth/login", json={"email": "viewer@example.com", "password": TEST_PASSWORD}
        ).json()
        r = c.post(
            AI + "/generate-caption",
            json={"topic": "abc"},
            headers={"Authorization": f"Bearer {token['access_token']}"},
        )
        assert r.status_code == 403


@pytest.mark.parametrize(
    ("factory_args", "http", "code"),
    [
        ((AIProviderUnavailableError("Ollama is not reachable"),), 503, "ai_provider_unavailable"),
        (("not json", "still not json"), 502, "ai_invalid_output"),
    ],
)
def test_failures_map_to_http_errors(make_client, user, brand, factory_args, http, code):
    with make_client(mock_factory(*factory_args)) as c:
        token = c.post(
            "/api/v1/auth/login", json={"email": "owner@example.com", "password": TEST_PASSWORD}
        ).json()
        h = {"Authorization": f"Bearer {token['access_token']}"}
        r = c.post(AI + "/generate-caption", json={"topic": "abc"}, headers=h)
        assert r.status_code == http
        err = r.json()["error"]
        assert err["code"] == code and err["details"]["job_id"]
        assert "Traceback" not in r.text
        job = c.get(f"{AI}/jobs/{err['details']['job_id']}", headers=h).json()
        assert job["job"]["status"] == "FAILED" and job["content_id"] is None
        assert c.get("/api/v1/contents", headers=h).json()["total"] == 0


@pytest.mark.parametrize(
    ("path", "body"),
    [
        ("/generate-caption", {"topic": "abc", "instructions": "x" * 1001}),
        ("/generate-caption", {"topic": "ab"}),
        ("/generate-caption", {"topic": "abc", "approve": True}),
        ("/ideas", {"count": 11}),
        ("/generate-carousel", {"topic": "abc", "slides": 11}),
        ("/generate-reels-script", {"topic": "abc", "target_seconds": 600}),
        ("/content-plan", {"start_date": "2026-10-12", "period": "year"}),
        ("/hashtags", {"topic": "abc", "count": 100}),
        ("/generate-caption", {"topic": "abc", "language": "de"}),
    ],
)
def test_request_limits(api, path, body):
    assert api.post(AI + path, json=body).status_code == 422


def test_language_not_enabled_for_brand(api):
    r = api.post(AI + "/generate-caption", json={"topic": "abc", "language": "ru"})
    assert r.status_code == 400 and r.json()["error"]["code"] == "language_not_supported"


def test_status_endpoint(api):
    data = api.get(AI + "/status").json()
    assert data["text"]["provider"] == "mock"
    assert data["publishing_available"] is False
    assert {m["status"] for m in data["media"]} == {"not_configured"}
    assert "CREATE_SCHEDULE" not in data["agent_permissions"]
    assert "ollama.test" not in str(data) and "secret" not in str(data).lower()


def test_evaluate_inline_and_saved(api):
    r = api.post(
        AI + "/evaluate-content",
        json={
            "content_type": "POST",
            "caption": "Natija 100% kafolatlanadi.",
            "cta": "Yozing",
            "hook": "h",
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert body["passed"] is False and "disclaimer" in body
    assert any(f["code"] == "guarantee_claim" for f in body["findings"])
    # The default brand bans "100% kafolat", which this caption contains.
    assert any(f["code"] == "banned_phrase" for f in body["findings"])

    cid = api.post(AI + "/generate-caption", json={"topic": "Minimalizm"}).json()["content_id"]
    r = api.post(AI + "/evaluate-content", json={"content_id": cid})
    assert r.status_code == 200 and r.json()["passed"] is True
    assert api.get(f"/api/v1/contents/{cid}").json()["status"] == "DRAFT"  # unchanged
    events = [e["action"] for e in api.get(f"/api/v1/contents/{cid}/history").json()["events"]]
    assert "AI_CONTENT_EVALUATED" in events
    assert api.post(AI + "/evaluate-content", json={"content_id": 999}).status_code == 404
    assert api.post(AI + "/evaluate-content", json={}).status_code == 422


def test_generate_image_not_configured(api, db):
    cid = api.post(AI + "/generate-caption", json={"topic": "Minimalizm"}).json()["content_id"]
    r = api.post(AI + "/generate-image", json={"content_id": cid})
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "not_configured" and data["assets_created"] == 0
    assert data["aspect_ratio"] == "4:5" and data["visual_prompt"]
    assert db.scalar(select(func.count()).select_from(ContentAsset)) == 0


def test_jobs_listing_and_ownership(api, make_client, db):
    job_id = api.post(AI + "/hashtags", json={"topic": "abc"}).json()["job"]["id"]
    assert [j["id"] for j in api.get(AI + "/jobs").json()] == [job_id]
    assert api.get(f"{AI}/jobs/{job_id}").json()["job"]["id"] == job_id
    assert api.get(f"{AI}/jobs/9999").status_code == 404
    # A viewer who did not create the job cannot see it.
    from app.core.security import hash_password
    from app.models import User
    from app.models.enums import UserRole

    db.add(
        User(
            email="other@example.com",
            password_hash=hash_password(TEST_PASSWORD),
            role=UserRole.VIEWER,
        )
    )
    db.commit()
    with make_client() as c:
        token = c.post(
            "/api/v1/auth/login", json={"email": "other@example.com", "password": TEST_PASSWORD}
        ).json()
        r = c.get(
            f"{AI}/jobs/{job_id}", headers={"Authorization": f"Bearer {token['access_token']}"}
        )
        assert r.status_code == 404


def test_celery_mode_returns_202(api, monkeypatch):
    import app.services.ai_content as module
    from app.core.config import get_settings
    from app.workers.celery_app import celery_app

    monkeypatch.setattr(get_settings(), "ai_jobs_mode", "celery")
    monkeypatch.setattr(module, "create_ai_provider", mock_factory())
    celery_app.conf.task_always_eager = True
    r = api.post(AI + "/hashtags", json={"topic": "abc"})
    assert r.status_code == 202
    job_id = r.json()["job"]["id"]
    assert api.get(f"{AI}/jobs/{job_id}").json()["job"]["status"] == "SUCCEEDED"


def test_openapi_ai_endpoints(api):
    spec = api.get("/openapi.json").json()
    ai_paths = {p: v for p, v in spec["paths"].items() if p.startswith(AI)}
    assert len(ai_paths) == 14  # + /regenerate (PHASE 4)
    for path, ops in ai_paths.items():
        for method, op in ops.items():
            assert op.get("security"), f"{method} {path}"
            assert "401" in op["responses"] and op.get("summary")
    assert not any("publish" in p or "approve" in p for p in ai_paths)


def test_provider_errors_do_not_leak_internal_urls(make_client, user, brand):
    from app.providers.ai.factory import create_ai_provider

    with make_client(create_ai_provider) as c:  # real Ollama provider -> unreachable host
        token = c.post(
            "/api/v1/auth/login", json={"email": "owner@example.com", "password": TEST_PASSWORD}
        ).json()
        h = {"Authorization": f"Bearer {token['access_token']}"}
        r = c.post(AI + "/generate-caption", json={"topic": "abc"}, headers=h)
        assert r.status_code == 503
        status = c.get(AI + "/status", headers=h)
        for text in (r.text, status.text):
            assert "ollama.test" not in text and "11434" not in text
