"""Connecting Instagram professional accounts via the official Meta OAuth flow.

Flow: start (one-time state bound to the user) -> Meta consent -> callback with
code+state -> state check -> code -> short-lived token -> required permissions
check -> long-lived token -> /me profile -> account + encrypted token stored.

Tokens never leave the backend unencrypted and are never logged or audited.
Instagram passwords are never requested: Meta handles the login.
"""

import base64
import hashlib
import hmac
import json
import logging
import secrets
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.agents.structured import run_sync
from app.core.actors import Actor, SystemActor
from app.core.config import get_settings
from app.core.crypto import EncryptionNotConfiguredError, TokenCipher
from app.core.errors import AppError, NotFoundError, PermissionDeniedError
from app.core.transaction import atomic
from app.integrations.meta.errors import MetaApiError, MetaErrorKind
from app.integrations.meta.instagram_login import InstagramLoginClient, MetaProfile
from app.models import (
    AnalyticsSnapshot,
    DataDeletionRequest,
    InstagramAccount,
    OAuthState,
    OAuthToken,
)
from app.models.base import utcnow
from app.models.enums import AuditAction, InstagramAccountType, MetaLoginMode
from app.repositories import InstagramAccountRepository, OAuthTokenRepository
from app.services.audit import AuditLogService
from app.services.guards import require_human_writer
from app.services.instagram import InstagramAccountService

logger = logging.getLogger(__name__)
MIN_REFRESH_AGE = timedelta(hours=24)  # Meta: token must be at least 24 hours old
REFRESH_ACTOR = SystemActor("instagram_token_refresher")
ACCOUNT_TYPES = {
    "BUSINESS": InstagramAccountType.BUSINESS,
    "MEDIA_CREATOR": InstagramAccountType.CREATOR,
    "CREATOR": InstagramAccountType.CREATOR,
}


def _hash(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


@dataclass(slots=True)
class ConnectResult:
    account: InstagramAccount
    scopes: list[str]
    expires_at: datetime | None
    warnings: list[str] = field(default_factory=list)


@dataclass(slots=True)
class AccountStatus:
    account: InstagramAccount
    token_expires_at: datetime | None
    token_last_refreshed_at: datetime | None
    scopes: list[str]
    missing_scopes: list[str]
    needs_reconnect: bool
    warnings: list[str]


class EncryptionKeysMissingError(AppError):
    status_code = 503


class InstagramOAuthService:
    def __init__(self, session: Session, client_factory=None) -> None:  # type: ignore[no-untyped-def]
        self.session = session
        self.settings = get_settings()
        self.audit = AuditLogService(session)
        self.accounts = InstagramAccountService(session, self.audit)
        self.client_factory = client_factory or (lambda: InstagramLoginClient(self.settings))

    # ------------------------------------------------------------------ start
    def start(self, actor: Actor) -> str:
        user = require_human_writer(self.session, actor)
        if not self.settings.meta_configured:
            raise MetaApiError(MetaErrorKind.NOT_CONFIGURED)
        try:  # fail before the user consents, not after the one-time code is spent
            TokenCipher.from_settings()
        except EncryptionNotConfiguredError as exc:
            raise EncryptionKeysMissingError(
                "TOKEN_ENCRYPTION_KEYS sozlanmagan: tokenlarni shifrlab saqlash uchun "
                ".env faylida kalit yarating (README, 11-bo‘lim).",
                code="token_encryption_not_configured",
            ) from exc
        state = secrets.token_urlsafe(32)
        with atomic(self.session):
            self.session.add(
                OAuthState(
                    state_hash=_hash(state),
                    user_id=user.id,
                    provider="instagram",
                    expires_at=utcnow()
                    + timedelta(minutes=self.settings.meta_oauth_state_ttl_minutes),
                )
            )
            self.audit.record(
                AuditAction.INSTAGRAM_OAUTH_STARTED,
                actor,
                details={"scopes": self.settings.meta_scopes},
            )
        client = self.client_factory()
        try:
            return client.authorize_url(state)
        finally:
            run_sync(client.aclose())

    # ------------------------------------------------------------------ callback
    def complete(
        self,
        actor: Actor,
        *,
        state: str,
        code: str | None,
        error: str | None = None,
        error_description: str | None = None,
    ) -> ConnectResult:
        user = require_human_writer(self.session, actor)
        self._consume_state(state, user.id)  # one-time, bound to this user
        try:
            if error or not code:
                raise AppError(
                    "Instagram ulanishi bekor qilindi yoki rad etildi."
                    + (f" ({error_description[:200]})" if error_description else ""),
                    code="instagram_oauth_denied",
                )
            short, long_lived, profile = run_sync(self._exchange(code))
            granted = short.permissions
            missing = [s for s in self.settings.meta_required_scopes if s not in granted]
            if granted and missing:
                raise AppError(
                    "Kerakli ruxsatlar berilmadi: "
                    + ", ".join(missing)
                    + ". Ulanishni qayta boshlang va barcha ruxsatlarni belgilang.",
                    code="instagram_permission_missing",
                    details={"missing": missing},
                )
            account_type = ACCOUNT_TYPES.get(
                (profile.account_type or "").upper(), InstagramAccountType.UNKNOWN
            )
            expires_at = (
                utcnow() + timedelta(seconds=long_lived.expires_in)
                if long_lived.expires_in > 0
                else None
            )
            with atomic(self.session):
                account = self.accounts.link_account(
                    actor,
                    ig_user_id=profile.ig_user_id,
                    username=profile.username,
                    account_type=account_type,
                    login_mode=MetaLoginMode.INSTAGRAM,
                )
                account.ig_app_scoped_id = profile.app_scoped_id or short.user_id
                account.profile_picture_url = (profile.profile_picture_url or "")[:1000] or None
                self.accounts.store_token(
                    account.id,
                    actor,
                    access_token=long_lived.access_token,
                    expires_at=expires_at,
                    scopes=granted or self.settings.meta_scopes,
                )
            return ConnectResult(
                account, granted, expires_at, self._warnings(account_type, granted)
            )
        except AppError as exc:
            self.audit.record_failure(
                AuditAction.INSTAGRAM_OAUTH_FAILED,
                actor,
                error=exc.message,
                details={
                    "code": exc.code,
                    **({"meta": exc.details} if isinstance(exc.details, dict) else {}),
                },
            )
            raise

    async def _exchange(self, code: str):  # type: ignore[no-untyped-def]
        client = self.client_factory()
        try:
            short = await client.exchange_code(code)
            long_lived = await client.exchange_long_lived(short.access_token)
            profile: MetaProfile = await client.get_me(long_lived.access_token)
            return short, long_lived, profile
        finally:
            await client.aclose()

    def _consume_state(self, state: str, user_id: int) -> None:
        with atomic(self.session):
            row = self.session.scalar(
                select(OAuthState)
                .where(OAuthState.state_hash == _hash(state or ""))
                .with_for_update()
            )
            invalid = (
                row is None
                or row.user_id != user_id
                or row.used_at is not None
                or row.expires_at <= utcnow()
            )
            if row is not None and row.used_at is None:
                row.used_at = utcnow()  # burn it even if it belongs to someone else
        # Raised after the block commits, so a stolen state stays burned.
        if invalid:
            raise AppError(
                "Ulanish so‘rovi yaroqsiz yoki muddati o‘tgan. Qaytadan boshlang.",
                code="instagram_oauth_state_invalid",
            )

    def _warnings(self, account_type: InstagramAccountType, granted: list[str]) -> list[str]:
        warnings = []
        if account_type == InstagramAccountType.CREATOR:
            warnings.append(
                "Creator akkaunt: Meta hujjatlari Stories'ni API orqali nashr qilishni "
                "faqat Business akkauntlar uchun aniq ko‘rsatadi."
            )
        if account_type == InstagramAccountType.UNKNOWN:
            warnings.append("Akkaunt turi aniqlanmadi.")
        optional = [s for s in self.settings.meta_scopes if granted and s not in granted]
        if optional:
            warnings.append("Ixtiyoriy ruxsatlar berilmagan: " + ", ".join(optional))
        return warnings

    # ------------------------------------------------------------------ status
    def statuses(self) -> list[AccountStatus]:
        out = []
        accounts = self.session.scalars(
            select(InstagramAccount)
            .where(InstagramAccount.deleted_at.is_(None))
            .order_by(InstagramAccount.id)
        ).all()
        for account in accounts:
            token = OAuthTokenRepository(self.session).get_active_for_account(account.id)
            scopes = (token.scopes or "").split() if token and token.scopes else []
            expired = bool(token and token.expires_at and token.expires_at <= utcnow())
            missing = [s for s in self.settings.meta_required_scopes if scopes and s not in scopes]
            warnings = self._warnings(account.account_type, scopes)
            if (
                token
                and token.expires_at
                and not expired
                and token.expires_at - utcnow() < timedelta(days=7)
            ):
                warnings.append("Token tez orada tugaydi; avtomatik yangilanadi.")
            out.append(
                AccountStatus(
                    account=account,
                    token_expires_at=token.expires_at if token else None,
                    token_last_refreshed_at=token.last_refreshed_at if token else None,
                    scopes=scopes,
                    missing_scopes=missing,
                    needs_reconnect=token is None or expired or bool(missing),
                    warnings=warnings,
                )
            )
        return out

    # ------------------------------------------------------------------ refresh
    def refresh_account(self, account_id: int, actor: Actor) -> OAuthToken:
        if not isinstance(actor, SystemActor):
            require_human_writer(self.session, actor)
        account = self.accounts.get(account_id)
        token_row = OAuthTokenRepository(self.session).get_active_for_account(account.id)
        if token_row is None:
            raise AppError("Akkaunt uchun faol token yo‘q; qayta ulang.", code="instagram_no_token")
        now = utcnow()
        if token_row.expires_at and token_row.expires_at <= now:
            raise MetaApiError(MetaErrorKind.TOKEN_EXPIRED)
        issued = token_row.last_refreshed_at or token_row.created_at
        if issued and now - issued < MIN_REFRESH_AGE:
            raise AppError(
                "Token 24 soatdan yangi; Meta uni hali yangilashga ruxsat bermaydi.",
                code="instagram_refresh_too_early",
            )
        plaintext = self.accounts.cipher.decrypt(token_row.token_ciphertext)

        async def _do():  # type: ignore[no-untyped-def]
            client = self.client_factory()
            try:
                return await client.refresh(plaintext)
            finally:
                await client.aclose()

        try:
            refreshed = run_sync(_do())
        except MetaApiError as exc:
            self.audit.record_failure(
                AuditAction.OAUTH_TOKEN_REFRESH_FAILED,
                actor,
                error=exc.message,
                details={"instagram_account_id": account.id, "kind": exc.kind.value},
            )
            raise
        expires_at = now + timedelta(seconds=refreshed.expires_in) if refreshed.expires_in else None
        with atomic(self.session):
            new = self.accounts.store_token(
                account.id,
                actor,
                access_token=refreshed.access_token,
                expires_at=expires_at,
                scopes=(token_row.scopes or "").split(),
            )
            self.audit.record(
                AuditAction.OAUTH_TOKEN_REFRESHED,
                actor,
                details={
                    "instagram_account_id": account.id,
                    "oauth_token_id": new.id,
                    "expires_at": expires_at.isoformat() if expires_at else None,
                },
            )
        return new

    def refresh_due(self) -> dict[str, int]:
        """Refresh tokens that expire within the window (run daily by Celery beat)."""
        window = timedelta(days=self.settings.meta_token_refresh_window_days)
        now = utcnow()
        result = {"checked": 0, "refreshed": 0, "failed": 0, "skipped": 0}
        rows = self.session.scalars(select(OAuthToken).where(OAuthToken.revoked_at.is_(None))).all()
        for row in rows:
            result["checked"] += 1
            issued = row.last_refreshed_at or row.created_at
            if (
                row.expires_at is None
                or row.expires_at <= now
                or row.expires_at - now > window
                or (issued and now - issued < MIN_REFRESH_AGE)
            ):
                result["skipped"] += 1
                continue
            try:
                self.refresh_account(row.instagram_account_id, REFRESH_ACTOR)
                result["refreshed"] += 1
            except (AppError, MetaApiError):
                result["failed"] += 1
        return result

    # ------------------------------------------------------------------ disconnect
    def disconnect(self, account_id: int, actor: Actor) -> None:
        user = require_human_writer(self.session, actor)
        account = self.accounts.get(account_id)
        if account.user_id != user.id and user.role.value != "OWNER":
            raise PermissionDeniedError("Only the owner can disconnect this account")
        with atomic(self.session):
            now = utcnow()
            for token in OAuthTokenRepository(self.session).list_active_for_account(account.id):
                token.revoked_at = now
                self.audit.record(
                    AuditAction.OAUTH_TOKEN_REVOKED,
                    actor,
                    details={"instagram_account_id": account.id, "oauth_token_id": token.id},
                )
            InstagramAccountRepository(self.session).soft_delete(account)
            self.audit.record(
                AuditAction.INSTAGRAM_ACCOUNT_DISCONNECTED,
                actor,
                details={"instagram_account_id": account.id},
            )

    # ------------------------------------------------------------------ Meta callbacks
    def parse_signed_request(self, signed_request: str) -> dict[str, Any]:
        """Verify Meta's signed_request (HMAC-SHA256 with the app secret)."""
        secret = self.settings.meta_app_secret.get_secret_value()
        if not secret:
            raise MetaApiError(MetaErrorKind.NOT_CONFIGURED)
        try:
            encoded_sig, payload = signed_request.split(".", 1)
            sig = _b64decode(encoded_sig)
            data = json.loads(_b64decode(payload))
        except (ValueError, json.JSONDecodeError) as exc:
            raise AppError("Invalid signed_request", code="invalid_signed_request") from exc
        if str(data.get("algorithm", "")).upper() != "HMAC-SHA256":
            raise AppError("Unsupported signature algorithm", code="invalid_signed_request")
        expected = hmac.new(secret.encode(), payload.encode(), hashlib.sha256).digest()
        if not hmac.compare_digest(sig, expected):
            raise AppError("Invalid signature", code="invalid_signed_request")
        if not data.get("user_id"):
            raise AppError("signed_request without user_id", code="invalid_signed_request")
        return data

    def _accounts_for_platform_id(self, platform_id: str) -> list[InstagramAccount]:
        return list(
            self.session.scalars(
                select(InstagramAccount).where(
                    (InstagramAccount.ig_user_id == platform_id)
                    | (InstagramAccount.ig_app_scoped_id == platform_id)
                )
            )
        )

    def deauthorize(self, signed_request: str) -> int:
        data = self.parse_signed_request(signed_request)
        platform_id = str(data["user_id"])
        actor = SystemActor("meta_deauthorize")
        with atomic(self.session):
            accounts = self._accounts_for_platform_id(platform_id)
            now = utcnow()
            for account in accounts:
                for token in OAuthTokenRepository(self.session).list_active_for_account(account.id):
                    token.revoked_at = now
            self.audit.record(
                AuditAction.INSTAGRAM_DEAUTHORIZED,
                actor,
                details={"platform_user_id": platform_id, "accounts": [a.id for a in accounts]},
            )
        return len(accounts)

    def data_deletion(self, signed_request: str) -> DataDeletionRequest:
        """Delete Instagram data for the user: tokens, insights, profile fields."""
        data = self.parse_signed_request(signed_request)
        platform_id = str(data["user_id"])
        actor = SystemActor("meta_data_deletion")
        code = secrets.token_hex(12)
        with atomic(self.session):
            accounts = self._accounts_for_platform_id(platform_id)
            ids = [a.id for a in accounts]
            if ids:
                self.session.execute(
                    delete(OAuthToken).where(OAuthToken.instagram_account_id.in_(ids))
                )
                self.session.execute(
                    delete(AnalyticsSnapshot).where(AnalyticsSnapshot.instagram_account_id.in_(ids))
                )
            for account in accounts:
                account.username = None
                account.profile_picture_url = None
                if account.deleted_at is None:
                    account.deleted_at = utcnow()
            record = DataDeletionRequest(
                confirmation_code=code,
                platform_user_id=platform_id,
                status="completed",
                details={"accounts": ids},
            )
            self.session.add(record)
            self.audit.record(
                AuditAction.INSTAGRAM_DATA_DELETION,
                actor,
                details={
                    "platform_user_id": platform_id,
                    "accounts": ids,
                    "confirmation_code": code,
                },
            )
        return record

    def deletion_status(self, code: str) -> DataDeletionRequest:
        row = self.session.scalar(
            select(DataDeletionRequest).where(DataDeletionRequest.confirmation_code == code)
        )
        if row is None:
            raise NotFoundError("Unknown confirmation code")
        return row


def _b64decode(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))
