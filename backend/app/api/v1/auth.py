from typing import Annotated

from fastapi import APIRouter, Depends, Request, status

from app.api.deps import CurrentUser, DbSession, get_token_payload
from app.core.config import get_settings
from app.core.ratelimit import client_ip
from app.models import User
from app.schemas.auth import LoginRequest, PasswordChangeRequest, TokenResponse, UserRead
from app.schemas.errors import error_responses
from app.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])

TokenPayload = Annotated[dict, Depends(get_token_payload)]


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Log in (rate limited; repeated failures lock the e-mail+IP for 15 minutes)",
    responses=error_responses(401, 422, 429),
)
def login(body: LoginRequest, request: Request, db: DbSession) -> TokenResponse:
    token, _ = AuthService(db).login(body.email, body.password, ip=client_ip(request))
    return TokenResponse(
        access_token=token, expires_in=get_settings().access_token_expire_minutes * 60
    )


@router.get("/me", response_model=UserRead, responses=error_responses(401))
def me(user: CurrentUser) -> User:
    return user


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Revoke this session's token server-side",
    responses=error_responses(401),
)
def logout(user: CurrentUser, payload: TokenPayload, db: DbSession) -> None:
    AuthService(db).logout(user, payload)


@router.post(
    "/logout-all",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Sign out every session of this user (all devices)",
    responses=error_responses(401),
)
def logout_all(user: CurrentUser, db: DbSession) -> None:
    AuthService(db).revoke_all_sessions(user)


@router.post(
    "/change-password",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Change password (min 12 chars); all sessions are signed out",
    responses=error_responses(400, 401, 422),
)
def change_password(body: PasswordChangeRequest, user: CurrentUser, db: DbSession) -> None:
    AuthService(db).change_password(user, body.current_password, body.new_password)
