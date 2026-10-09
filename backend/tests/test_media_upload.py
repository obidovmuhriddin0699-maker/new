"""PHASE 8: media upload, URL attach and public serving."""

import logging

import pytest

from app.core.config import get_settings
from app.core.logging import SecretRedactionFilter, install_secret_filters
from app.services.media_storage import MediaStorage, jpeg_size, sniff
from tests.conftest import TEST_PASSWORD, make_content
from tests.meta_publish_fake import tiny_jpeg, tiny_mp4


@pytest.fixture
def api(client, auth_headers, monkeypatch):
    monkeypatch.setattr(get_settings(), "media_public_base_url", "https://media.example")
    client.headers.update(auth_headers)
    return client


def upload(api, content_id, data, version, content_type="application/octet-stream"):
    return api.post(
        f"/api/v1/contents/{content_id}/assets/upload?expected_version={version}",
        content=data,
        headers={"Content-Type": content_type},
    )


def test_sniff_and_jpeg_size():
    assert sniff(tiny_jpeg()) == "jpg" and jpeg_size(tiny_jpeg(640, 800)) == (640, 800)
    assert sniff(tiny_mp4()) == "mp4"
    assert sniff(b"\x89PNG\r\n\x1a\n" + b"0" * 20) is None


def test_upload_jpeg_creates_version_and_is_served(api, db, human):
    content = make_content(db, human)
    r = upload(api, content.id, tiny_jpeg(1080, 1350), content.version)
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["version"] == content.version + 1  # media change = new version
    asset = body["assets"][0]
    assert asset["kind"] == "IMAGE" and asset["mime_type"] == "image/jpeg"
    assert (asset["width"], asset["height"]) == (1080, 1350)
    assert asset["public_url"].startswith("https://media.example/media/")
    name = asset["public_url"].rsplit("/", 1)[1]

    anonymous = api.get(f"/api/v1/media/{name}", headers={"Authorization": ""})
    assert anonymous.status_code == 200  # Meta's servers fetch it without a session
    assert anonymous.headers["content-type"] == "image/jpeg"
    assert anonymous.headers["x-content-type-options"] == "nosniff"
    assert anonymous.content == tiny_jpeg(1080, 1350)


def test_upload_video(api, db, human):
    content = make_content(db, human)
    r = upload(api, content.id, tiny_mp4(), content.version)
    assert r.status_code == 201 and r.json()["assets"][0]["kind"] == "VIDEO"


@pytest.mark.parametrize(
    "data",
    [
        b"",
        b"\x89PNG\r\n\x1a\n" + b"0" * 64,
        b"<script>alert(1)</script>",
        b"\xff\xd8\xff" + b"0" * 8,
    ],
)
def test_upload_rejects_bad_files(api, db, human, data):
    content = make_content(db, human)
    r = upload(api, content.id, data, content.version, "image/jpeg")  # header is ignored
    assert r.status_code == 422 and r.json()["error"]["code"] == "media_rejected"


def test_upload_size_limit(api, db, human, monkeypatch):
    monkeypatch.setattr(get_settings(), "media_max_image_mb", 1)
    monkeypatch.setattr(get_settings(), "media_max_video_mb", 1)
    content = make_content(db, human)
    big = tiny_jpeg() + b"\x00" * (1024 * 1024 + 10)
    r = upload(api, content.id, big, content.version)
    assert r.status_code == 422 and "katta" in r.json()["error"]["message"]


def test_upload_with_stale_version_leaves_no_file(api, db, human):
    content = make_content(db, human)
    root = MediaStorage().root
    before = set(root.glob("*")) if root.exists() else set()
    r = upload(api, content.id, tiny_jpeg(), content.version + 5)
    assert r.status_code == 409
    after = set(root.glob("*")) if root.exists() else set()
    assert after == before


def test_upload_requires_writer(client, db, human, viewer):
    content = make_content(db, human)
    login = client.post(
        "/api/v1/auth/login", json={"email": "viewer@example.com", "password": TEST_PASSWORD}
    )
    viewer_headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
    r = client.post(
        f"/api/v1/contents/{content.id}/assets/upload?expected_version=1",
        content=tiny_jpeg(),
        headers=viewer_headers,
    )
    assert r.status_code == 403


@pytest.mark.parametrize("name", ["../../etc/passwd", "x.jpg", "a" * 30 + ".png", "%2e%2e"])
def test_media_route_rejects_bad_names(client, name):
    assert client.get(f"/api/v1/media/{name}").status_code == 404


def test_attach_https_url(api, db, human):
    content = make_content(db, human)
    r = api.post(
        f"/api/v1/contents/{content.id}/assets",
        json={
            "expected_version": content.version,
            "kind": "IMAGE",
            "public_url": "https://cdn.example/photo.JPG?v=2",
        },
    )
    assert r.status_code == 201, r.text
    assert r.json()["assets"][0]["mime_type"] == "image/jpeg"
    bad = api.post(
        f"/api/v1/contents/{content.id}/assets",
        json={
            "expected_version": r.json()["version"],
            "kind": "IMAGE",
            "public_url": "http://cdn.example/photo.jpg",
        },
    )
    assert bad.status_code == 422


def test_remove_asset(api, db, human):
    content = make_content(db, human)
    r = upload(api, content.id, tiny_jpeg(), content.version).json()
    asset_id = r["assets"][0]["id"]
    d = api.delete(
        f"/api/v1/contents/{content.id}/assets/{asset_id}?expected_version={r['version']}"
    )
    assert d.status_code == 200 and d.json()["assets"] == []


def test_secret_filter_redacts_tokens_at_any_level(caplog):
    install_secret_filters()
    caplog.set_level(logging.DEBUG)
    logging.getLogger("httpx").warning(
        "HTTP Request: GET https://graph.instagram.com/x?fields=a&access_token=IGAA-abc123 ok"
    )
    assert "IGAA-abc123" not in caplog.text and "access_token=***" in caplog.text
    record = logging.LogRecord("httpx", 20, "", 0, "client_secret=%s", ("s3cr3t",), None)
    SecretRedactionFilter().filter(record)
    assert record.getMessage() == "client_secret=***"
