"""Management commands.

python -m app.cli create-admin --email you@example.com
"""

import argparse
import getpass
import sys

from sqlalchemy import select

from app.core.database import get_sessionmaker
from app.core.security import hash_password, normalize_login_email
from app.models import User
from app.models.enums import UserRole


def create_admin(email: str, password: str | None, full_name: str | None) -> int:
    try:
        email = normalize_login_email(email)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    password = password or getpass.getpass("Password (min 12 chars): ")
    if len(password) < 12:
        print("Password must be at least 12 characters.", file=sys.stderr)
        return 1
    with get_sessionmaker()() as db:
        if db.scalar(select(User).where(User.email == email.lower())):
            print(f"User {email} already exists.", file=sys.stderr)
            return 1
        db.add(
            User(
                email=email.lower(),
                password_hash=hash_password(password),
                full_name=full_name,
                role=UserRole.OWNER,
            )
        )
        db.commit()
    print(f"Created owner user {email.lower()}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="app.cli")
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("create-admin")
    p.add_argument("--email", required=True)
    p.add_argument("--password", help="omit to be prompted (recommended)")
    p.add_argument("--full-name")
    s = sub.add_parser("seed", help="load safe development data (idempotent)")
    s.add_argument("--admin-email", help="defaults to SEED_ADMIN_EMAIL or admin@example.com")
    sub.add_parser("refresh-instagram-tokens", help="refresh tokens close to expiry")
    sub.add_parser("publish-due", help="publish due schedules once (what Celery beat does)")
    sub.add_parser("reconcile-publishing", help="settle schedules stuck in PROCESSING")
    sub.add_parser("sync-insights", help="pull Instagram insights now (read-only)")
    sub.add_parser(
        "db-app-role",
        help="create/update the least-privilege app DB role (APP_DB_USER, APP_DB_PASSWORD)",
    )
    sub.add_parser(
        "rotate-token-keys",
        help="re-encrypt stored OAuth tokens with the first TOKEN_ENCRYPTION_KEYS key",
    )
    sub.add_parser("weekly-report", help="create the analyst report for last week")
    sub.add_parser(
        "migrate",
        help="alembic upgrade head under a PostgreSQL advisory lock (safe with several replicas)",
    )
    args = parser.parse_args(argv)
    if args.command == "create-admin":
        return create_admin(args.email, args.password, args.full_name)
    if args.command == "seed":
        return seed(args.admin_email)
    if args.command == "refresh-instagram-tokens":
        from app.services.instagram_oauth import InstagramOAuthService

        with get_sessionmaker()() as db:
            print(InstagramOAuthService(db).refresh_due())
        return 0
    if args.command in ("publish-due", "reconcile-publishing"):
        from app.services.publish import PublishService

        with get_sessionmaker()() as db:
            service = PublishService(db)
            result = (
                service.process_due()
                if args.command == "publish-due"
                else service.reconcile_stale()
            )
            print(result)
        return 0
    if args.command == "sync-insights":
        from dataclasses import asdict

        from app.services.analytics_sync import AnalyticsSyncService

        with get_sessionmaker()() as db:
            for r in AnalyticsSyncService(db).sync_all():
                print(asdict(r))
        return 0
    if args.command == "db-app-role":
        import os

        role, password = os.environ.get("APP_DB_USER", ""), os.environ.get("APP_DB_PASSWORD", "")
        if not role or len(password) < 16:
            print("APP_DB_USER and APP_DB_PASSWORD (min 16 chars) are required")
            return 2
        setup_app_db_role(role, password)
        print(f"app role {role!r}: privileges applied")
        return 0
    if args.command == "rotate-token-keys":
        print(f"re-encrypted {rotate_token_keys()} token(s)")
        return 0
    if args.command == "migrate":
        return migrate()
    if args.command == "weekly-report":
        from app.services.analytics_report import ANALYST_ACTOR, AnalyticsReportService

        with get_sessionmaker()() as db:
            report = AnalyticsReportService(db).create_weekly(ANALYST_ACTOR)
            print(f"report #{report.id} ({report.source}, {report.status})\n{report.summary}")
        return 0
    return 1


MIGRATION_LOCK_ID = 7_302_412_001  # arbitrary, constant: one migration runner at a time


def migrate() -> int:
    """Upgrade the schema to head. On PostgreSQL an advisory lock serialises concurrent
    runners (several replicas / a pre-deploy step racing a start command)."""
    from pathlib import Path

    from alembic import command
    from alembic.config import Config
    from sqlalchemy import text

    from app.core.database import get_engine

    ini = Path(__file__).resolve().parent.parent / "alembic.ini"
    cfg = Config(str(ini))
    engine = get_engine()
    if engine.dialect.name != "postgresql":
        command.upgrade(cfg, "head")
        print("migrations applied")
        return 0
    with engine.connect() as conn:
        conn.execute(text("SELECT pg_advisory_lock(:id)"), {"id": MIGRATION_LOCK_ID})
        try:
            command.upgrade(cfg, "head")
        finally:
            conn.execute(text("SELECT pg_advisory_unlock(:id)"), {"id": MIGRATION_LOCK_ID})
    print("migrations applied")
    return 0


def seed(admin_email: str | None) -> int:
    from app.seed import run_seed

    with get_sessionmaker()() as db:
        result = run_seed(db, admin_email=admin_email)
    print(f"Admin: {result.admin_email} ({'created' if result.admin_created else 'exists'})")
    if result.generated_password:
        print("Generated admin password (shown once, store it safely):")
        print(f"  {result.generated_password}")
    print(f"Brand profile id: {result.brand_profile_id}")
    print(
        f"Example draft content id: {result.content_id} "
        f"({'created' if result.content_created else 'exists'})"
    )
    return 0


def rotate_token_keys() -> int:
    """Key rotation: put the NEW key first in TOKEN_ENCRYPTION_KEYS (keep the old one after
    it), run this, then remove the old key. Tokens are never printed."""
    from app.core.crypto import TokenCipher
    from app.models import OAuthToken

    cipher = TokenCipher.from_settings()
    count = 0
    with get_sessionmaker()() as db:
        for token in db.query(OAuthToken).all():
            token.token_ciphertext = cipher.rotate(token.token_ciphertext)
            count += 1
        db.commit()
    return count


def setup_app_db_role(role: str, password: str) -> None:
    """Least-privilege database role for the running application (PostgreSQL only).

    Run by the migrate service as the database owner, after ``alembic upgrade head``.
    The app role can read/write rows but owns nothing: it cannot alter tables or drop the
    audit-log trigger, and it may only SELECT/INSERT audit_logs. Idempotent."""
    from psycopg import sql
    from sqlalchemy import create_engine

    from app.core.config import get_settings

    url = get_settings().effective_database_url
    if not url.startswith("postgresql"):
        raise SystemExit("db-app-role needs PostgreSQL")
    engine = create_engine(url)
    raw = engine.raw_connection()
    try:
        cur = raw.cursor()
        role_id = sql.Identifier(role)
        cur.execute("SELECT 1 FROM pg_roles WHERE rolname = %s", (role,))
        if cur.fetchone() is None:
            cur.execute(
                sql.SQL(
                    "CREATE ROLE {} LOGIN PASSWORD {} NOSUPERUSER NOCREATEDB NOCREATEROLE"
                ).format(role_id, sql.Literal(password))
            )
        else:
            cur.execute(sql.SQL("ALTER ROLE {} PASSWORD {}").format(role_id, sql.Literal(password)))
        cur.execute("SELECT current_database()")
        db_name = cur.fetchone()[0]
        statements = [
            "GRANT CONNECT ON DATABASE {db} TO {role}",
            "GRANT USAGE ON SCHEMA public TO {role}",
            "REVOKE CREATE ON SCHEMA public FROM PUBLIC",
            "GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO {role}",
            "GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO {role}",
            # History is append-only for the app (the trigger also blocks the owner).
            "REVOKE UPDATE, DELETE, TRUNCATE ON audit_logs FROM {role}",
        ]
        cur.execute("SELECT to_regclass('public.alembic_version') IS NOT NULL")
        if cur.fetchone()[0]:
            statements += [
                "REVOKE ALL ON alembic_version FROM {role}",
                "GRANT SELECT ON alembic_version TO {role}",
            ]
        for statement in statements:
            cur.execute(sql.SQL(statement).format(db=sql.Identifier(db_name), role=role_id))
        raw.commit()
    finally:
        raw.close()
        engine.dispose()


if __name__ == "__main__":
    raise SystemExit(main())
