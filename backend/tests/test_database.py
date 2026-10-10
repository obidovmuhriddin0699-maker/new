import os

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect, select, text

from app.core.database import check_database, get_engine
from app.models import Base, Content, User
from app.models.enums import ContentStatus, ContentType

BACKEND_DIR = os.path.dirname(os.path.dirname(__file__))
EXPECTED_TABLES = {
    "users",
    "instagram_accounts",
    "oauth_tokens",
    "contents",
    "content_assets",
    "content_schedules",
    "approvals",
    "analytics_snapshots",
    "content_performance",
    "brand_profiles",
    "ai_jobs",
    "audit_logs",
    "system_settings",
    "content_versions",
}


def _alembic_config(url: str) -> Config:
    cfg = Config(os.path.join(BACKEND_DIR, "alembic.ini"))
    cfg.set_main_option("script_location", os.path.join(BACKEND_DIR, "alembic"))
    cfg.set_main_option("sqlalchemy.url", url)
    return cfg


def test_database_connection():
    ok, err = check_database()
    assert ok, err
    with get_engine().connect() as conn:
        assert conn.execute(text("SELECT 1")).scalar() == 1


def test_crud_roundtrip(db):
    user = User(email="a@example.com", password_hash="x")
    db.add(user)
    db.flush()
    db.add(Content(content_type=ContentType.REELS, topic="Minimalist bedroom"))
    db.commit()
    content = db.scalar(select(Content))
    assert content.status == ContentStatus.DRAFT
    assert content.version == 1
    assert content.created_at is not None and content.updated_at is not None
    assert content.deleted_at is None


def test_enum_stored_as_value(db):
    db.add(Content(content_type=ContentType.POST))
    db.commit()
    raw = db.execute(text("SELECT status, language FROM contents")).one()
    assert tuple(raw) == ("DRAFT", "uz")


def _run_migrations(url: str) -> None:
    cfg = _alembic_config(url)
    command.upgrade(cfg, "head")
    engine = create_engine(url)
    tables = set(inspect(engine).get_table_names())
    assert EXPECTED_TABLES <= tables
    assert "alembic_version" in tables
    engine.dispose()

    command.downgrade(cfg, "base")
    engine = create_engine(url)
    assert set(inspect(engine).get_table_names()) <= {"alembic_version"}
    engine.dispose()
    command.upgrade(cfg, "head")


def test_alembic_upgrade_downgrade_sqlite(tmp_path):
    _run_migrations(f"sqlite:///{tmp_path / 'migr.db'}")


def test_migration_matches_models(tmp_path):
    """Alembic head must produce exactly the schema the models declare."""
    from alembic.autogenerate import compare_metadata
    from alembic.runtime.migration import MigrationContext

    url = f"sqlite:///{tmp_path / 'diff.db'}"
    command.upgrade(_alembic_config(url), "head")
    engine = create_engine(url)
    with engine.connect() as conn:
        diff = compare_metadata(MigrationContext.configure(conn), Base.metadata)
    engine.dispose()
    assert diff == []


@pytest.mark.postgres
@pytest.mark.skipif(not os.getenv("TEST_POSTGRES_URL"), reason="TEST_POSTGRES_URL not set")
def test_alembic_upgrade_downgrade_postgres():
    _run_migrations(os.environ["TEST_POSTGRES_URL"])


def test_partial_unique_index_present_after_migration(tmp_path):
    url = f"sqlite:///{tmp_path / 'idx.db'}"
    command.upgrade(_alembic_config(url), "head")
    engine = create_engine(url)
    indexes = {ix["name"]: ix for ix in inspect(engine).get_indexes("approvals")}
    engine.dispose()
    assert indexes["uq_approvals_active_approved"]["unique"]


def test_migration_refuses_unbindable_legacy_approvals(tmp_path):
    """91ed60cfe649 must stop rather than invent hashes for pre-existing approvals."""
    url = f"sqlite:///{tmp_path / 'legacy.db'}"
    cfg = _alembic_config(url)
    command.upgrade(cfg, "22d94eda60d4")
    engine = create_engine(url)
    with engine.begin() as conn:
        conn.execute(
            text(
                "INSERT INTO users (email, password_hash, role, is_active) "
                "VALUES ('a@example.com', 'h', 'OWNER', 1)"
            )
        )
        conn.execute(
            text(
                "INSERT INTO contents (content_type, status, version, language, "
                "hashtags, created_by) VALUES ('POST', 'APPROVED', 1, 'uz', '[]', "
                "'HUMAN')"
            )
        )
        conn.execute(
            text(
                "INSERT INTO approvals (content_id, content_version, decision, "
                "decided_by_user_id, channel) VALUES (1, 1, 'APPROVED', 1, 'WEB')"
            )
        )
    engine.dispose()
    with pytest.raises(RuntimeError, match="must be empty|requires 'approvals'"):
        command.upgrade(cfg, "head")
