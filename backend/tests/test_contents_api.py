from datetime import UTC, datetime, timedelta

import jwt
import pytest

from app.core.config import get_settings
from tests.conftest import TEST_PASSWORD

BASE = "/api/v1/contents"
NEW = {
    "content_type": "CAROUSEL",
    "language": "uz",
    "topic": "Minimalist yotoqxona",
    "caption": "Minimalizm — bu to‘g‘ri tanlov.",
    "hashtags": ["interiordesign", "#minimalism", "#minimalism"],
    "aspect_ratio": "4:5",
}


def _token(user_id: int, **claims) -> str:
    s = get_settings()
    payload = {
        "sub": str(user_id),
        "type": "access",
        "exp": datetime.now(UTC) + timedelta(minutes=5),
        **claims,
    }
    return jwt.encode(payload, s.jwt_secret_key.get_secret_value(), algorithm=s.jwt_algorithm)


@pytest.fixture
def viewer_headers(client, viewer):
    resp = client.post(
        "/api/v1/auth/login", json={"email": "viewer@example.com", "password": TEST_PASSWORD}
    )
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


def _create(client, headers, **overrides):
    resp = client.post(BASE, json={**NEW, **overrides}, headers=headers)
    assert resp.status_code == 201, resp.text
    return resp.json()


def test_full_create_review_approve_flow(client, auth_headers):
    c = _create(client, auth_headers)
    assert c["status"] == "DRAFT" and c["version"] == 1
    assert c["hashtags"] == ["#interiordesign", "#minimalism"]  # normalised, deduplicated
    assert c["publish_authorized"] is False

    r = client.post(f"{BASE}/{c['id']}/submit-review", headers=auth_headers)
    assert r.status_code == 200 and r.json()["status"] == "READY_FOR_REVIEW"

    r = client.post(f"{BASE}/{c['id']}/approve", json={"expected_version": 1}, headers=auth_headers)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["created"] is True
    assert body["content"]["status"] == "APPROVED"
    assert body["content"]["publish_authorized"] is True
    assert body["approval"]["content_version"] == 1

    again = client.post(
        f"{BASE}/{c['id']}/approve", json={"expected_version": 1}, headers=auth_headers
    )
    assert again.status_code == 200 and again.json()["created"] is False

    # Editing approved content -> v2, back to review, previous approval invalid
    r = client.patch(
        f"{BASE}/{c['id']}", json={"expected_version": 1, "caption": "v2"}, headers=auth_headers
    )
    assert r.status_code == 200
    assert r.json()["version"] == 2
    assert r.json()["status"] == "READY_FOR_REVIEW"
    assert r.json()["publish_authorized"] is False

    # Approving with the old version number is refused
    r = client.post(f"{BASE}/{c['id']}/approve", json={"expected_version": 1}, headers=auth_headers)
    assert r.status_code == 409
    assert r.json()["error"]["code"] == "version_mismatch"

    h = client.get(f"{BASE}/{c['id']}/history", headers=auth_headers).json()
    assert [v["version"] for v in h["versions"]] == [1, 2]
    assert h["approvals"][0]["invalidated_at"] is not None
    actions = [e["action"] for e in h["events"]]
    for expected in (
        "CONTENT_CREATED",
        "CONTENT_APPROVED",
        "CONTENT_APPROVAL_INVALIDATED",
        "CONTENT_VERSION_CREATED",
        "CONTENT_UPDATED",
    ):
        assert expected in actions


def test_reject_and_request_edit(client, auth_headers):
    c = _create(client, auth_headers)
    client.post(f"{BASE}/{c['id']}/submit-review", headers=auth_headers)
    r = client.post(
        f"{BASE}/{c['id']}/request-edit",
        json={"expected_version": 1, "comment": "CTA ni o‘zgartiring"},
        headers=auth_headers,
    )
    assert r.json()["status"] == "EDIT_REQUESTED"
    client.patch(
        f"{BASE}/{c['id']}", json={"expected_version": 1, "cta": "Saqlang"}, headers=auth_headers
    )
    client.post(f"{BASE}/{c['id']}/submit-review", headers=auth_headers)
    r = client.post(f"{BASE}/{c['id']}/reject", json={"expected_version": 2}, headers=auth_headers)
    assert r.json()["status"] == "REJECTED"
    r = client.post(f"{BASE}/{c['id']}/approve", json={"expected_version": 2}, headers=auth_headers)
    assert r.status_code == 409
    assert r.json()["error"]["code"] == "invalid_state_transition"


def test_cannot_approve_draft(client, auth_headers):
    c = _create(client, auth_headers)
    r = client.post(f"{BASE}/{c['id']}/approve", json={"expected_version": 1}, headers=auth_headers)
    assert r.status_code == 409


def test_list_and_get(client, auth_headers):
    _create(client, auth_headers)
    _create(client, auth_headers, content_type="REELS")
    r = client.get(BASE, params={"content_type": "REELS"}, headers=auth_headers)
    assert r.json()["total"] == 1
    r = client.get(BASE, params={"status": "DRAFT", "limit": 1}, headers=auth_headers)
    assert r.json()["total"] == 2 and len(r.json()["items"]) == 1
    assert client.get(f"{BASE}/999", headers=auth_headers).status_code == 404


@pytest.mark.parametrize(
    ("method", "path"),
    [
        ("get", ""),
        ("post", ""),
        ("get", "/1"),
        ("patch", "/1"),
        ("post", "/1/submit-review"),
        ("post", "/1/request-edit"),
        ("post", "/1/approve"),
        ("post", "/1/reject"),
        ("get", "/1/history"),
    ],
)
def test_all_endpoints_require_authentication(client, method, path):
    r = getattr(client, method)(f"{BASE}{path}")
    assert r.status_code == 401


def test_viewer_can_read_but_not_approve_or_write(client, auth_headers, viewer_headers):
    c = _create(client, auth_headers)
    client.post(f"{BASE}/{c['id']}/submit-review", headers=auth_headers)
    assert client.get(f"{BASE}/{c['id']}", headers=viewer_headers).status_code == 200
    r = client.post(
        f"{BASE}/{c['id']}/approve", json={"expected_version": 1}, headers=viewer_headers
    )
    assert r.status_code == 403 and r.json()["error"]["code"] == "approval_forbidden"
    assert client.post(BASE, json=NEW, headers=viewer_headers).status_code == 403


def test_non_human_token_cannot_approve(client, auth_headers, user):
    c = _create(client, auth_headers)
    client.post(f"{BASE}/{c['id']}/submit-review", headers=auth_headers)
    for claims in ({}, {"actor": "agent"}, {"actor": "system"}):
        headers = {"Authorization": f"Bearer {_token(user.id, **claims)}"}
        r = client.post(f"{BASE}/{c['id']}/approve", json={"expected_version": 1}, headers=headers)
        assert r.status_code == 401
    assert client.get(f"{BASE}/{c['id']}", headers=auth_headers).json()["status"] == (
        "READY_FOR_REVIEW"
    )


@pytest.mark.parametrize(
    "payload",
    [
        {**NEW, "status": "PUBLISHED"},
        {**NEW, "version": 5},
        {**NEW, "caption": "x" * 2201},
        {**NEW, "hashtags": [f"#t{i}" for i in range(31)]},
        {**NEW, "hashtags": ["#two words"]},
        {**NEW, "aspect_ratio": "wide"},
        {**NEW, "content_type": "TWEET"},
    ],
)
def test_create_validation(client, auth_headers, payload):
    assert client.post(BASE, json=payload, headers=auth_headers).status_code == 422


def test_patch_requires_expected_version_and_forbids_status(client, auth_headers):
    c = _create(client, auth_headers)
    assert (
        client.patch(f"{BASE}/{c['id']}", json={"caption": "x"}, headers=auth_headers).status_code
        == 422
    )
    assert (
        client.patch(
            f"{BASE}/{c['id']}",
            json={"expected_version": 1, "status": "APPROVED"},
            headers=auth_headers,
        ).status_code
        == 422
    )


def test_responses_do_not_expose_sensitive_fields(client, auth_headers):
    c = _create(client, auth_headers)
    text = client.get(f"{BASE}/{c['id']}/history", headers=auth_headers).text
    for forbidden in ("password", "token_ciphertext", "jwt_secret", "storage_path"):
        assert forbidden not in text


def test_openapi_documents_security_and_errors(client):
    spec = client.get("/openapi.json").json()
    paths = {p: v for p, v in spec["paths"].items() if p.startswith(BASE)}
    # collection, item, 4 decision/review actions, history, schedule (PHASE 4),
    # readiness, diff, revoke-approval (PHASE 6), publish, publish-preview, assets,
    # assets/upload, assets/{asset_id} (PHASE 8)
    assert len(paths) == 16
    for path, ops in spec["paths"].items():
        if not path.startswith(BASE):
            continue
        for method, op in ops.items():
            assert op.get("security"), f"{method} {path} lacks security"
            assert "401" in op["responses"], f"{method} {path} lacks 401"
            assert op.get("summary"), f"{method} {path} lacks summary"
            ok = next(c for c in op["responses"] if c.startswith("2"))
            if ok != "204":  # 204 No Content has no body by definition
                assert "schema" in op["responses"][ok]["content"]["application/json"]
    approve = spec["paths"][f"{BASE}/{{content_id}}/approve"]["post"]
    assert {"401", "403", "404", "409", "422"} <= set(approve["responses"])
    assert "ErrorResponse" in spec["components"]["schemas"]
    publish = spec["paths"][f"{BASE}/{{content_id}}/publish"]["post"]
    assert {"401", "403", "404", "409", "422"} <= set(publish["responses"])
