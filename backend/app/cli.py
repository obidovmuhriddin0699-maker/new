"""Management commands.

python -m app.cli create-admin --email you@example.com
"""

import argparse
import getpass
import sys

from sqlalchemy import select

from app.core.database import get_sessionmaker
from app.core.security import hash_password
from app.models import User
from app.models.enums import UserRole


def create_admin(email: str, password: str | None, full_name: str | None) -> int:
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
    args = parser.parse_args(argv)
    if args.command == "create-admin":
        return create_admin(args.email, args.password, args.full_name)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
