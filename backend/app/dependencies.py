import hmac
import os
import time
from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models import AuthSession, Membership, User
from backend.app.security import hash_token


SESSION_COOKIE_NAME = "session"
CSRF_COOKIE_NAME = "csrf_token"
SESSION_MAX_AGE = 60 * 60 * 24 * 7
COOKIE_SECURE = os.getenv("COOKIE_SECURE", "false").lower() == "true"
DbSession = Annotated[Session, Depends(get_db)]


def get_auth_session(request: Request, db: DbSession) -> AuthSession:
    token = request.cookies.get(SESSION_COOKIE_NAME)
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    auth_session = db.scalar(
        select(AuthSession).where(AuthSession.token_hash == hash_token(token))
    )
    if auth_session is None or auth_session.expires_at <= int(time.time()):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired")
    return auth_session


CurrentSession = Annotated[AuthSession, Depends(get_auth_session)]


def get_current_user(auth_session: CurrentSession, db: DbSession) -> User:
    user = db.get(User, auth_session.user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def require_csrf(
    request: Request,
    auth_session: CurrentSession,
) -> AuthSession:
    cookie_token = request.cookies.get(CSRF_COOKIE_NAME, "")
    header_token = request.headers.get("X-CSRF-Token", "")
    if (
        not cookie_token
        or not header_token
        or not hmac.compare_digest(cookie_token, header_token)
        or not hmac.compare_digest(hash_token(cookie_token), auth_session.csrf_token_hash)
    ):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="CSRF validation failed")
    return auth_session


CsrfSession = Annotated[AuthSession, Depends(require_csrf)]


def require_membership(
    workspace_id: str,
    user: CurrentUser,
    db: DbSession,
) -> Membership:
    membership = db.scalar(
        select(Membership).where(
            Membership.workspace_id == workspace_id,
            Membership.user_id == user.id,
        )
    )
    if membership is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found")
    return membership


def require_workspace_admin(
    workspace_id: str,
    user: CurrentUser,
    db: DbSession,
) -> Membership:
    membership = require_membership(workspace_id, user, db)
    if membership.role not in {"owner", "admin"}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Workspace admin required")
    return membership
