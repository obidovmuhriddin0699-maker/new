import time
import uuid

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.dependencies import (
    CSRF_COOKIE_NAME,
    SESSION_COOKIE_NAME,
    SESSION_MAX_AGE,
    CurrentSession,
    CurrentUser,
    CsrfSession,
)
from backend.app.config import cookie_secure
from backend.app.models import AuthSession, Membership, User, Workspace
from backend.app.schemas import Credentials, CurrentUserResponse, UserResponse, WorkspaceResponse
from backend.app.security import generate_token, hash_password, hash_token, verify_password


router = APIRouter(prefix="/auth", tags=["auth"])


def set_session_cookies(response: Response, token: str, csrf_token: str) -> None:
    secure = cookie_secure()
    response.set_cookie(
        SESSION_COOKIE_NAME,
        token,
        max_age=SESSION_MAX_AGE,
        httponly=True,
        secure=secure,
        samesite="lax",
        path="/",
    )
    response.set_cookie(
        CSRF_COOKIE_NAME,
        csrf_token,
        max_age=SESSION_MAX_AGE,
        httponly=False,
        secure=secure,
        samesite="lax",
        path="/",
    )


def create_session(db: Session, user: User, response: Response) -> None:
    token = generate_token()
    csrf_token = generate_token()
    db.add(
        AuthSession(
            id=str(uuid.uuid4()),
            token_hash=hash_token(token),
            csrf_token_hash=hash_token(csrf_token),
            user_id=user.id,
            expires_at=int(time.time()) + SESSION_MAX_AGE,
        )
    )
    set_session_cookies(response, token, csrf_token)


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(
    credentials: Credentials,
    response: Response,
    db: Session = Depends(get_db),
) -> User:
    if db.scalar(select(User.id).where(User.email == credentials.email)) is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    user = User(
        id=str(uuid.uuid4()),
        email=credentials.email,
        password_hash=hash_password(credentials.password),
    )
    db.add(user)
    create_session(db, user, response)
    db.commit()
    return user


@router.post("/login", response_model=UserResponse)
def login(
    credentials: Credentials,
    response: Response,
    db: Session = Depends(get_db),
) -> User:
    user = db.scalar(select(User).where(User.email == credentials.email))
    if user is None or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    create_session(db, user, response)
    db.commit()
    return user


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    response: Response,
    auth_session: CsrfSession,
    db: Session = Depends(get_db),
) -> Response:
    db.delete(auth_session)
    db.commit()
    secure = cookie_secure()
    response.delete_cookie(SESSION_COOKIE_NAME, path="/", secure=secure, samesite="lax")
    response.delete_cookie(CSRF_COOKIE_NAME, path="/", secure=secure, samesite="lax")
    response.status_code = status.HTTP_204_NO_CONTENT
    return response


@router.get("/me", response_model=CurrentUserResponse)
def current_user(
    auth_session: CurrentSession,
    user: CurrentUser,
    db: Session = Depends(get_db),
) -> CurrentUserResponse:
    rows = db.execute(
        select(Workspace, Membership.role)
        .join(Membership, Membership.workspace_id == Workspace.id)
        .where(Membership.user_id == user.id)
        .order_by(Workspace.name)
    ).all()
    return CurrentUserResponse(
        id=user.id,
        email=user.email,
        active_workspace_id=auth_session.active_workspace_id,
        workspaces=[
            WorkspaceResponse(id=workspace.id, name=workspace.name, role=role)
            for workspace, role in rows
        ],
    )
