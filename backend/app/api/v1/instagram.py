"""Instagram account connection (official Meta OAuth, Instagram Login) and Meta callbacks."""

from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Form, status
from pydantic import BaseModel, ConfigDict, Field

from app.api.deps import DbSession, HumanActorDep, limit_per_ip, limit_per_user
from app.core.config import get_settings
from app.core.errors import NotFoundError
from app.core.ratelimit import META_CALLBACK, OAUTH_START, QUOTA_CHECK
from app.integrations.meta.capabilities import CAPABILITIES
from app.models import InstagramAccount
from app.schemas.errors import error_responses
from app.schemas.publish import CapabilityRead, PublishingLimitRead
from app.services.instagram_oauth import InstagramOAuthService
from app.services.publish import PublishService

router = APIRouter(prefix="/instagram", tags=["instagram"])


class AccountRead(BaseModel):
    id: int
    ig_user_id: str
    username: str | None
    account_type: str
    profile_picture_url: str | None
    connected_at: datetime | None
    token_expires_at: datetime | None
    token_last_refreshed_at: datetime | None
    scopes: list[str]
    missing_scopes: list[str]
    needs_reconnect: bool
    warnings: list[str]


class InstagramStatus(BaseModel):
    configured: bool = Field(description="META_APP_ID, META_APP_SECRET and META_REDIRECT_URI set")
    login_mode: str
    graph_api_version: str
    requested_scopes: list[str]
    required_scopes: list[str]
    redirect_uri: str | None
    dry_run: bool
    accounts: list[AccountRead]


class StartResponse(BaseModel):
    authorize_url: str


class CallbackRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")

    state: str = Field(min_length=10, max_length=200)
    code: str | None = Field(default=None, max_length=2000)
    error: str | None = Field(default=None, max_length=200)
    error_reason: str | None = Field(default=None, max_length=200)
    error_description: str | None = Field(default=None, max_length=500)


class ConnectResponse(BaseModel):
    account: AccountRead
    warnings: list[str]


def _account(s) -> AccountRead:  # type: ignore[no-untyped-def]
    a = s.account
    return AccountRead(
        id=a.id,
        ig_user_id=a.ig_user_id,
        username=a.username,
        account_type=a.account_type.value,
        profile_picture_url=a.profile_picture_url,
        connected_at=a.connected_at,
        token_expires_at=s.token_expires_at,
        token_last_refreshed_at=s.token_last_refreshed_at,
        scopes=s.scopes,
        missing_scopes=s.missing_scopes,
        needs_reconnect=s.needs_reconnect,
        warnings=s.warnings,
    )


@router.get(
    "/status",
    response_model=InstagramStatus,
    summary="Instagram connection status",
    description="No secrets: app secret and tokens are never returned.",
    responses=error_responses(401),
)
def instagram_status(db: DbSession, _: HumanActorDep) -> InstagramStatus:
    s = get_settings()
    return InstagramStatus(
        configured=s.meta_configured,
        login_mode=s.meta_login_mode,
        graph_api_version=s.meta_graph_api_version,
        requested_scopes=s.meta_scopes,
        required_scopes=s.meta_required_scopes,
        redirect_uri=s.meta_redirect_uri or None,
        dry_run=s.meta_dry_run,
        accounts=[_account(x) for x in InstagramOAuthService(db).statuses()],
    )


@router.post(
    "/oauth/start",
    response_model=StartResponse,
    summary="Start the official Meta OAuth flow",
    description="Returns the Instagram authorization URL with a one-time `state` bound "
    "to the current user (expires in META_OAUTH_STATE_TTL_MINUTES).",
    responses=error_responses(401, 403) | {503: {"description": "Meta app not configured"}},
    dependencies=[limit_per_user(OAUTH_START)],
)
def oauth_start(db: DbSession, actor: HumanActorDep) -> StartResponse:
    return StartResponse(authorize_url=InstagramOAuthService(db).start(actor))


@router.post(
    "/oauth/callback",
    response_model=ConnectResponse,
    summary="Finish the OAuth flow (called by the panel's callback page)",
    responses=error_responses(400, 401, 403, 422)
    | {502: {"description": "Meta API error (user-friendly message in error)"}},
    dependencies=[limit_per_user(OAUTH_START)],
)
def oauth_callback(body: CallbackRequest, db: DbSession, actor: HumanActorDep) -> ConnectResponse:
    service = InstagramOAuthService(db)
    result = service.complete(
        actor,
        state=body.state,
        code=body.code,
        error=body.error,
        error_description=body.error_description or body.error_reason,
    )
    status_row = next(x for x in service.statuses() if x.account.id == result.account.id)
    return ConnectResponse(account=_account(status_row), warnings=result.warnings)


@router.post(
    "/accounts/{account_id}/refresh-token",
    response_model=AccountRead,
    summary="Refresh the long-lived token now",
    responses=error_responses(400, 401, 403, 404) | {502: {"description": "Meta error"}},
    dependencies=[limit_per_user(OAUTH_START)],
)
def refresh_token(account_id: int, db: DbSession, actor: HumanActorDep) -> AccountRead:
    service = InstagramOAuthService(db)
    service.refresh_account(account_id, actor)
    return _account(next(x for x in service.statuses() if x.account.id == account_id))


@router.delete(
    "/accounts/{account_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Disconnect an Instagram account (tokens revoked locally)",
    responses=error_responses(401, 403, 404),
)
def disconnect(account_id: int, db: DbSession, actor: HumanActorDep) -> None:
    InstagramOAuthService(db).disconnect(account_id, actor)


@router.get(
    "/capabilities",
    response_model=list[CapabilityRead],
    summary="What the Content Publishing API supports (unsupported items are never faked)",
    responses=error_responses(401),
)
def capabilities(_: HumanActorDep) -> list[CapabilityRead]:
    return [
        CapabilityRead(key=c.key, label=c.label, supported=c.supported, note=c.note)
        for c in CAPABILITIES
    ]


@router.get(
    "/accounts/{account_id}/publishing-limit",
    response_model=PublishingLimitRead,
    summary="Live content publishing quota from Meta (read-only)",
    description="Calls `content_publishing_limit`. Meta's pages disagree on the quota "
    "(50 vs 100 posts / 24 h), so the live value is shown.",
    responses=error_responses(401, 404, 429) | {502: {"description": "Meta error"}},
    dependencies=[limit_per_user(QUOTA_CHECK)],
)
def publishing_limit(account_id: int, db: DbSession, _: HumanActorDep) -> PublishingLimitRead:
    account = db.get(InstagramAccount, account_id)
    if account is None or account.deleted_at is not None:
        raise NotFoundError("Instagram account not found")
    limit = PublishService(db).publishing_limit(account)
    return PublishingLimitRead(
        instagram_account_id=account.id,
        username=account.username,
        quota_usage=limit.quota_usage,
        quota_total=limit.quota_total,
        remaining=limit.remaining,
        quota_duration_seconds=limit.quota_duration_seconds,
        from_meta=limit.from_meta,
    )


# ---------------------------------------------------------------- Meta → server callbacks
class DeletionResponse(BaseModel):
    url: str
    confirmation_code: str


@router.post(
    "/meta/deauthorize",
    summary="Meta deauthorize callback (signed_request)",
    responses=error_responses(400),
    dependencies=[limit_per_ip(META_CALLBACK)],
)
def meta_deauthorize(
    db: DbSession, signed_request: Annotated[str, Form(max_length=4000)]
) -> dict[str, bool]:
    InstagramOAuthService(db).deauthorize(signed_request)
    return {"ok": True}


@router.post(
    "/meta/data-deletion",
    response_model=DeletionResponse,
    summary="Meta data deletion request callback (signed_request)",
    responses=error_responses(400),
    dependencies=[limit_per_ip(META_CALLBACK)],
)
def meta_data_deletion(
    db: DbSession, signed_request: Annotated[str, Form(max_length=4000)]
) -> DeletionResponse:
    record = InstagramOAuthService(db).data_deletion(signed_request)
    base = get_settings().panel_public_url.rstrip("/")
    return DeletionResponse(
        url=f"{base}/api/meta/data-deletion-status?code={record.confirmation_code}",
        confirmation_code=record.confirmation_code,
    )


@router.get(
    "/meta/data-deletion/{code}",
    summary="Public data deletion status",
    responses=error_responses(404),
)
def meta_data_deletion_status(code: str, db: DbSession) -> dict[str, str]:
    record = InstagramOAuthService(db).deletion_status(code[:64])
    return {
        "confirmation_code": record.confirmation_code,
        "status": record.status,
        "requested_at": record.created_at.isoformat(),
    }
