from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.actors import HumanActor
from app.core.database import get_db
from app.core.errors import AuthenticationError
from app.core.logging import request_id_var
from app.core.security import decode_access_token
from app.models import User
from app.models.enums import ApprovalChannel

DbSession = Annotated[Session, Depends(get_db)]
_bearer = HTTPBearer(auto_error=False)


def get_current_user(
    db: DbSession,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
) -> User:
    if credentials is None:
        raise AuthenticationError("Not authenticated")
    payload = decode_access_token(credentials.credentials)
    if payload.get("actor") != "human":
        # Only interactive human sessions get user tokens; anything else is refused.
        raise AuthenticationError("Token is not a human session")
    try:
        user_id = int(payload["sub"])
    except (KeyError, ValueError) as exc:
        raise AuthenticationError("Invalid token") from exc
    user = db.scalar(select(User).where(User.id == user_id, User.deleted_at.is_(None)))
    if user is None or not user.is_active:
        raise AuthenticationError("User not found or inactive")
    from app.services.auth import AuthService

    if AuthService(db).is_revoked(user, payload):
        raise AuthenticationError("Session has been signed out", code="session_revoked")
    return user


def get_token_payload(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
) -> dict:
    if credentials is None:
        raise AuthenticationError("Not authenticated")
    return decode_access_token(credentials.credentials)


CurrentUser = Annotated[User, Depends(get_current_user)]


def get_human_actor(user: CurrentUser) -> HumanActor:
    """The verified human behind this request (web panel channel)."""
    return HumanActor(user_id=user.id, channel=ApprovalChannel.WEB, request_id=request_id_var.get())


HumanActorDep = Annotated[HumanActor, Depends(get_human_actor)]


# ------------------------------------------------------------------ rate limits
def limit_per_user(limit):  # type: ignore[no-untyped-def]
    """Dependency: count this request against ``limit`` for the signed-in user."""
    from app.core.ratelimit import get_limiter

    def dep(actor: HumanActorDep) -> None:
        get_limiter().check(limit, f"user:{actor.user_id}")

    return Depends(dep)


def limit_per_ip(limit):  # type: ignore[no-untyped-def]
    """Dependency: count this request against ``limit`` for the client IP."""
    from fastapi import Request

    from app.core.ratelimit import client_ip, get_limiter

    def dep(request: Request) -> None:
        get_limiter().check(limit, f"ip:{client_ip(request)}")

    return Depends(dep)
