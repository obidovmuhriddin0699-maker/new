from datetime import UTC, date, datetime, timedelta

import pytest
from fastapi.testclient import TestClient

from app.api.v1.ai import get_provider_factory
from app.models import AnalyticsSnapshot, ContentPerformance, InstagramAccount
from app.models.base import utcnow
from app.providers.ai.base import AIProviderUnavailableError
from tests.conftest import TEST_PASSWORD, make_approved, make_content, make_ready, mock_factory


def _login(c, email="owner@example.com"):
    token = c.post("/api/v1/auth/login", json={"email": email, "password": TEST_PASSWORD}).json()
    c.headers["Authorization"] = f"Bearer {token['access_token']}"
    return c


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
        yield _login(c)


def test_dashboard_counts_without_analytics(api, db, human):
    make_content(db, human)
    make_ready(db, human)
    make_approved(db, human)
    data = api.get("/api/v1/dashboard/summary").json()
    assert data["total"] == 3
    assert data["drafts"] == 1 and data["pending_approval"] == 1
    assert data["by_status"]["APPROVED"] == 1
    assert data["reach"] is None and data["engagement_rate"] is None
    assert data["analytics_available"] is False  # nothing is estimated


def test_dashboard_uses_real_analytics_only(api, db, human, user):
    content = make_content(db, human)
    account = InstagramAccount(user_id=user.id, ig_user_id="ig-x")
    db.add(account)
    db.flush()
    db.add(
        AnalyticsSnapshot(
            instagram_account_id=account.id,
            scope="account",
            period="week",  # the dashboard shows the 7-day window
            captured_at=utcnow(),
            metrics={"reach": 1234},
        )
    )
    db.add(ContentPerformance(content_id=content.id, metrics={}, engagement_rate=0.05))
    db.commit()
    data = api.get("/api/v1/dashboard/summary").json()
    assert data["reach"] == 1234 and data["engagement_rate"] == pytest.approx(0.05)
    assert data["analytics_available"] is True


def test_schedule_unschedule_and_calendar(api, db, human):
    content = make_approved(db, human)
    when = (datetime.now(UTC) + timedelta(days=2)).replace(microsecond=0)
    r = api.post(f"/api/v1/contents/{content.id}/schedule", json={"scheduled_at": when.isoformat()})
    assert r.status_code == 200, r.text
    assert r.json()["content_version"] == 1 and "publish worker" in r.json()["note"]
    again = api.post(
        f"/api/v1/contents/{content.id}/schedule", json={"scheduled_at": when.isoformat()}
    )
    assert again.json()["created"] is False and again.json()["id"] == r.json()["id"]
    summary = api.get("/api/v1/dashboard/summary").json()
    assert summary["scheduled"] == 1 and summary["upcoming"][0]["content_id"] == content.id

    cal = api.get(
        "/api/v1/calendar",
        params={
            "start": date.today().isoformat(),
            "end": (date.today() + timedelta(7)).isoformat(),
        },
    )
    items = cal.json()["items"]
    assert [(i["content_id"], i["kind"]) for i in items] == [(content.id, "scheduled")]

    assert api.delete(f"/api/v1/contents/{content.id}/schedule").json()["status"] == "APPROVED"
    cal = api.get(
        "/api/v1/calendar",
        params={
            "start": date.today().isoformat(),
            "end": (date.today() + timedelta(7)).isoformat(),
        },
    )
    assert cal.json()["items"] == []


def test_schedule_requires_approval(api, db, human):
    content = make_ready(db, human)
    when = (datetime.now(UTC) + timedelta(days=1)).isoformat()
    r = api.post(f"/api/v1/contents/{content.id}/schedule", json={"scheduled_at": when})
    assert r.status_code == 409


def test_planned_dates_in_calendar_and_range_limits(api, db, human):
    content = make_content(db, human)
    r = api.patch(
        f"/api/v1/contents/{content.id}", json={"expected_version": 1, "planned_date": "2026-11-03"}
    )
    assert r.json()["planned_date"] == "2026-11-03" and r.json()["version"] == 1  # not versioned
    cal = api.get("/api/v1/calendar", params={"start": "2026-11-01", "end": "2026-11-30"}).json()
    assert cal["items"][0]["kind"] == "planned" and cal["items"][0]["date"] == "2026-11-03"
    assert (
        api.get("/api/v1/calendar", params={"start": "2026-01-01", "end": "2026-06-01"}).status_code
        == 400
    )
    assert (
        api.get("/api/v1/calendar", params={"start": "2026-02-01", "end": "2026-01-01"}).status_code
        == 400
    )


def test_delete_content(api, db, human):
    content = make_approved(db, human)
    assert api.delete(f"/api/v1/contents/{content.id}").status_code == 204
    assert api.get(f"/api/v1/contents/{content.id}").status_code == 404
    assert api.get("/api/v1/dashboard/summary").json()["total"] == 0


def test_audit_log_admin_only(api, make_client, db, human, viewer):
    make_approved(db, human)
    data = api.get("/api/v1/audit-logs", params={"limit": 3}).json()
    # login (PHASE 10 audits it) + created, version, submit, approve
    assert data["total"] == 5 and len(data["items"]) == 3
    assert data["items"][0]["id"] > data["items"][-1]["id"]  # newest first
    filtered = api.get("/api/v1/audit-logs", params={"action": "CONTENT_APPROVED"}).json()
    assert {i["action"] for i in filtered["items"]} == {"CONTENT_APPROVED"}
    with make_client() as c:
        assert _login(c, "viewer@example.com").get("/api/v1/audit-logs").status_code == 403


def test_brand_profile_api(api, make_client, brand, viewer):
    assert api.get("/api/v1/brand-profiles").json()[0]["name"] == "Test Studio"
    r = api.patch(
        f"/api/v1/brand-profiles/{brand.id}",
        json={"preferred_ctas": [" Save ", "Save", "Share"], "languages": ["uz"]},
    )
    assert r.status_code == 200
    assert r.json()["preferred_ctas"] == ["Save", "Share"] and r.json()["languages"] == ["uz"]
    assert (
        api.patch(f"/api/v1/brand-profiles/{brand.id}", json={"languages": ["de"]}).status_code
        == 422
    )
    assert (
        api.patch(f"/api/v1/brand-profiles/{brand.id}", json={"is_default": True}).status_code
        == 422
    )
    created = api.post("/api/v1/brand-profiles", json={"name": "Second", "make_default": True})
    assert created.status_code == 201 and created.json()["is_default"] is True
    events = api.get("/api/v1/audit-logs", params={"action": "BRAND_PROFILE_UPDATED"}).json()
    assert events["total"] == 1
    with make_client() as c:
        v = _login(c, "viewer@example.com")
        assert v.get("/api/v1/brand-profiles").status_code == 200
        assert v.patch(f"/api/v1/brand-profiles/{brand.id}", json={"niche": "x"}).status_code == 403


def test_assets_library(api, db, human):
    from app.models.enums import AssetKind
    from app.services import AssetInput, ContentService

    content = make_content(db, human)
    ContentService(db).add_asset(
        content.id,
        human,
        expected_version=1,
        asset=AssetInput(kind=AssetKind.IMAGE, width=1080, height=1350),
    )
    data = api.get("/api/v1/assets").json()
    assert data["total"] == 1 and data["items"][0]["content_id"] == content.id
    assert "storage_path" not in data["items"][0]


def _generate(api, path="/api/v1/ai/generate-carousel", **body):
    r = api.post(path, json={"topic": "Minimalist yotoqxona", **body})
    assert r.status_code == 200, r.text
    return r.json()


def test_regenerate_from_review_creates_new_version(api):
    first = _generate(api, submit_for_review=True)
    cid = first["content_id"]
    assert first["content_status"] == "READY_FOR_REVIEW"
    r = api.post(
        "/api/v1/ai/regenerate",
        json={"content_id": cid, "expected_version": 1, "instructions": "Qisqaroq"},
    )
    assert r.status_code == 200, r.text
    assert r.json()["content_status"] == "READY_FOR_REVIEW"
    content = api.get(f"/api/v1/contents/{cid}").json()
    assert content["version"] == 2 and content["publish_authorized"] is False
    history = api.get(f"/api/v1/contents/{cid}/history").json()
    actions = [e["action"] for e in history["events"]]
    assert "CONTENT_EDIT_REQUESTED" in actions and "CONTENT_GENERATION_STARTED" in actions
    assert history["approvals"][0]["decision"] == "EDIT_REQUESTED"
    assert history["approvals"][0]["comment"] == "Qisqaroq"
    assert history["versions"][1]["ai_metadata"]["regenerated_from_version"] == 1


def test_regenerate_rules(api, db, human):
    approved = make_approved(db, human)
    r = api.post("/api/v1/ai/regenerate", json={"content_id": approved.id, "expected_version": 1})
    assert r.status_code == 400 and r.json()["error"]["code"] == "invalid_state_transition"
    draft = _generate(api)
    r = api.post(
        "/api/v1/ai/regenerate", json={"content_id": draft["content_id"], "expected_version": 9}
    )
    assert r.status_code == 409
    assert (
        api.post(
            "/api/v1/ai/regenerate", json={"content_id": 999, "expected_version": 1}
        ).status_code
        == 404
    )


def test_regenerate_failure_marks_content_failed(make_client, brand, db, human):
    from app.services.ai_content import AIContentService, JobType

    content = (
        AIContentService(db, provider_factory=mock_factory())
        .execute(AIContentService(db).request(JobType.POST, {"topic": "abc"}, human).id)
        .content
    )
    with make_client(mock_factory(AIProviderUnavailableError("down"))) as c:
        r = _login(c).post(
            "/api/v1/ai/regenerate", json={"content_id": content.id, "expected_version": 1}
        )
        assert r.status_code == 503
        assert c.get(f"/api/v1/contents/{content.id}").json()["status"] == "FAILED"
        assert c.get(f"/api/v1/contents/{content.id}").json()["version"] == 1


def test_plan_drafts_get_planned_dates(api):
    r = api.post(
        "/api/v1/ai/content-plan", json={"start_date": "2026-11-02", "save_as_drafts": True}
    )
    items = r.json()["result"]["items"]
    cal = api.get("/api/v1/calendar", params={"start": "2026-11-02", "end": "2026-11-08"}).json()
    assert sorted(i["content_id"] for i in cal["items"]) == sorted(i["content_id"] for i in items)
    assert {i["kind"] for i in cal["items"]} == {"planned"}


@pytest.mark.parametrize(
    ("method", "path"),
    [
        ("get", "/api/v1/dashboard/summary"),
        ("get", "/api/v1/calendar?start=2026-01-01&end=2026-01-02"),
        ("get", "/api/v1/audit-logs"),
        ("get", "/api/v1/brand-profiles"),
        ("get", "/api/v1/assets"),
        ("post", "/api/v1/contents/1/schedule"),
        ("delete", "/api/v1/contents/1"),
        ("post", "/api/v1/ai/regenerate"),
    ],
)
def test_panel_endpoints_require_auth(make_client, method, path):
    with make_client() as c:
        assert getattr(c, method)(path).status_code == 401


def test_panel_and_ai_routes_cannot_publish(api):
    paths = api.get("/openapi.json").json()["paths"]
    assert not any("publish" in p for p in paths if p.startswith(("/api/v1/panel", "/api/v1/ai")))
