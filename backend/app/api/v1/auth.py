import secrets

from fastapi import APIRouter
from sqlalchemy import select

from app.api.deps import CurrentUser, DbSession
from app.core.config import get_settings
from app.core.errors import AuthenticationError
from app.core.security import create_access_token, hash_password, verify_password
from app.models import User
from app.schemas.auth import LoginRequest, TokenResponse, UserRead

router = APIRouter(prefix="/auth", tags=["auth"])

# Hash of a random secret: keeps login timing similar for unknown emails.
_DUMMY_HASH = hash_password(secrets.token_urlsafe(32))


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest, db: DbSession) -> TokenResponse:
    user = db.scalar(
        select(User).where(User.email == body.email.lower(), User.deleted_at.is_(None))
    )
    if user is None:
        verify_password(body.password, _DUMMY_HASH)
        raise AuthenticationError("Invalid email or password")
    if not verify_password(body.password, user.password_hash) or not user.is_active:
        raise AuthenticationError("Invalid email or password")
    settings = get_settings()
    return TokenResponse(
        access_token=create_access_token(str(user.id), {"role": user.role.value}),
        expires_in=settings.access_token_expire_minutes * 60,
    )


@router.get("/me", response_model=UserRead)
def me(user: CurrentUser) -> User:
    return user
