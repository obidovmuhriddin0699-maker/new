import pytest
from sqlalchemy import func, select

from app.core.config import get_settings
from app.core.security import verify_password
from app.models import Content, InstagramAccount, OAuthToken, User
from app.models.enums import ContentStatus
from app.repositories import (
    BrandProfileRepository,
    ContentAssetRepository,
    SystemSettingRepository,
)
from app.seed import run_seed


def test_seed_creates_safe_dev_data_and_is_idempotent(db, monkeypatch):
    monkeypatch.setenv("SEED_ADMIN_PASSWORD", "seed-password-from-env")
    first = run_seed(db)
    assert first.admin_created and first.generated_password is None
    admin = db.scalars(select(User)).one()
    assert verify_password("seed-password-from-env", admin.password_hash)
    brand = BrandProfileRepository(db).get_default()
    assert brand.name == "Muxriddin Design"
    assert "Soxta mijoz fikrlari yaratma" in brand.forbidden_rules
    content = db.get(Content, first.content_id)
    assert content.status == ContentStatus.DRAFT
    assert len(ContentAssetRepository(db).list_for_content(content.id)) == 3
    assert SystemSettingRepository(db).get_value("content.default_language") == "uz"
    # No Instagram accounts or tokens are ever seeded.
    assert db.scalar(select(func.count()).select_from(InstagramAccount)) == 0
    assert db.scalar(select(func.count()).select_from(OAuthToken)) == 0

    second = run_seed(db)
    assert not second.admin_created and not second.content_created
    assert db.scalar(select(func.count()).select_from(Content)) == 1
    assert db.scalar(select(func.count()).select_from(User)) == 1


def test_seed_generates_password_when_not_provided(db, monkeypatch):
    monkeypatch.delenv("SEED_ADMIN_PASSWORD", raising=False)
    result = run_seed(db, admin_email="Dev@Example.com")
    assert result.admin_email == "dev@example.com"
    assert result.generated_password and len(result.generated_password) >= 20


def test_seed_rejects_short_password(db, monkeypatch):
    monkeypatch.setenv("SEED_ADMIN_PASSWORD", "short")
    with pytest.raises(ValueError):
        run_seed(db)


def test_seed_refuses_production(db, monkeypatch):
    monkeypatch.setattr(get_settings(), "app_env", "production")
    with pytest.raises(RuntimeError):
        run_seed(db)


def test_seeded_admin_can_log_in(client, monkeypatch):
    from app.core.database import get_sessionmaker

    monkeypatch.setenv("SEED_ADMIN_PASSWORD", "seed-password-from-env")
    with get_sessionmaker()() as session:
        result = run_seed(session)
    resp = client.post(
        "/api/v1/auth/login",
        json={"email": result.admin_email, "password": "seed-password-from-env"},
    )
    assert resp.status_code == 200, resp.text


@pytest.mark.parametrize("email", ["admin@muxriddin.local", "not-an-email"])
def test_seed_rejects_emails_that_cannot_log_in(db, email):
    with pytest.raises(ValueError):
        run_seed(db, admin_email=email)


def test_cli_create_admin_rejects_unloggable_email(capsys):
    from app.cli import main

    assert main(["create-admin", "--email", "x@host.local", "--password", "a" * 16]) == 1
    assert "Invalid email" in capsys.readouterr().err
