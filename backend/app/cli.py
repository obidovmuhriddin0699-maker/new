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
    return 1


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


if __name__ == "__main__":
    raise SystemExit(main())
