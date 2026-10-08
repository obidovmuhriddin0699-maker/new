from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect


def test_initial_migration_creates_all_application_tables(
    monkeypatch,
    tmp_path: Path,
) -> None:
    database_path = tmp_path / "migration.sqlite"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{database_path.as_posix()}")
    config = Config("alembic.ini")

    command.upgrade(config, "head")

    engine = create_engine(f"sqlite:///{database_path.as_posix()}")
    try:
        tables = set(inspect(engine).get_table_names())
    finally:
        engine.dispose()

    assert {
        "users",
        "workspaces",
        "memberships",
        "auth_sessions",
        "workspace_billing",
        "workspace_usage",
        "workflows",
        "workflow_phases",
        "telegram_accounts",
        "telegram_link_challenges",
        "alembic_version",
    } <= tables
