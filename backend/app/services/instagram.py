"""Instagram account records and encrypted OAuth token storage.

No Meta HTTP call here: ``InstagramOAuthService`` (PHASE 7) feeds tokens
obtained from the official OAuth flow into ``store_token``. Tokens are
encrypted before they touch the database and never appear in audit logs.
Agents can never read, store or revoke tokens.
"""

from collections.abc import Sequence
from datetime import datetime

from sqlalchemy.orm import Session

from app.core.actors import Actor, AgentActor, HumanActor, SystemActor
from app.core.crypto import TokenCipher
from app.core.errors import NotFoundError, PermissionDeniedError
from app.core.transaction import atomic
from app.models import InstagramAccount, OAuthToken
from app.models.base import utcnow
from app.models.enums import AuditAction, InstagramAccountType, MetaLoginMode
from app.repositories import InstagramAccountRepository, OAuthTokenRepository
from app.services.audit import AuditLogService
from app.services.guards import require_human_writer


class InstagramAccountService:
    def __init__(
        self,
        session: Session,
        audit: AuditLogService | None = None,
        cipher: TokenCipher | None = None,
    ) -> None:
        self.session = session
        self.audit = audit or AuditLogService(session)
        self.accounts = InstagramAccountRepository(session)
        self.tokens = OAuthTokenRepository(session)
        self._cipher = cipher

    @property
    def cipher(self) -> TokenCipher:
        if self._cipher is None:
            self._cipher = TokenCipher.from_settings()
        return self._cipher

    def list_for_user(self, user_id: int) -> Sequence[InstagramAccount]:
        return self.accounts.list_for_user(user_id)

    def get(self, account_id: int) -> InstagramAccount:
        account = self.accounts.get(account_id)
        if account is None:
            raise NotFoundError("Instagram account not found")
        return account

    def link_account(
        self,
        actor: Actor,
        *,
        ig_user_id: str,
        username: str | None,
        account_type: InstagramAccountType = InstagramAccountType.UNKNOWN,
        login_mode: MetaLoginMode = MetaLoginMode.INSTAGRAM,
    ) -> InstagramAccount:
        """Create (or restore a soft-deleted) account record for the current human."""
        with atomic(self.session):
            user = require_human_writer(self.session, actor)
            account = self.accounts.get_by_ig_user_id(ig_user_id, include_deleted=True)
            if account is None:
                account = InstagramAccount(ig_user_id=ig_user_id, user_id=user.id)
                self.session.add(account)
            elif account.user_id != user.id and account.deleted_at is None:
                raise PermissionDeniedError("This Instagram account is linked to another user")
            account.user_id = user.id
            account.username = username
            account.account_type = account_type
            account.login_mode = login_mode
            account.deleted_at = None
            account.connected_at = utcnow()
            self.session.flush()
            self.audit.record(
                AuditAction.INSTAGRAM_ACCOUNT_LINKED,
                actor,
                details={"instagram_account_id": account.id, "username": username},
            )
            return account

    def store_token(
        self,
        account_id: int,
        actor: Actor,
        *,
        access_token: str,
        expires_at: datetime | None,
        scopes: Sequence[str] = (),
        token_type: str = "long_lived",  # noqa: S107 - token kind label, not a secret
    ) -> OAuthToken:
        self._require_token_manager(actor)
        with atomic(self.session):
            account = self.get(account_id)
            now = utcnow()
            for old in self.tokens.list_active_for_account(account.id):
                old.revoked_at = now
            token = self.tokens.add(
                OAuthToken(
                    instagram_account_id=account.id,
                    token_ciphertext=self.cipher.encrypt(access_token),
                    token_type=token_type,
                    scopes=" ".join(scopes) or None,
                    expires_at=expires_at,
                    last_refreshed_at=now,
                )
            )
            self.audit.record(
                AuditAction.OAUTH_TOKEN_STORED,
                actor,
                details={
                    "instagram_account_id": account.id,
                    "oauth_token_id": token.id,
                    "scopes": list(scopes),
                    "expires_at": expires_at.isoformat() if expires_at else None,
                },
            )
            return token

    def get_access_token(self, account_id: int, actor: Actor) -> str | None:
        """Decrypt for backend use (publish/insights workers) — never for agents or APIs."""
        if not isinstance(actor, SystemActor):
            raise PermissionDeniedError("Only backend services may read OAuth tokens")
        token = self.tokens.get_active_for_account(account_id)
        if token is None:
            return None
        if token.expires_at is not None and token.expires_at <= utcnow():
            return None
        return self.cipher.decrypt(token.token_ciphertext)

    def disconnect(self, account_id: int, actor: Actor) -> None:
        with atomic(self.session):
            user = require_human_writer(self.session, actor)
            account = self.get(account_id)
            if account.user_id != user.id:
                raise PermissionDeniedError("Not your Instagram account")
            now = utcnow()
            for token in self.tokens.list_active_for_account(account.id):
                token.revoked_at = now
                self.audit.record(
                    AuditAction.OAUTH_TOKEN_REVOKED,
                    actor,
                    details={"instagram_account_id": account.id, "oauth_token_id": token.id},
                )
            self.accounts.soft_delete(account)
            self.audit.record(
                AuditAction.INSTAGRAM_ACCOUNT_DISCONNECTED,
                actor,
                details={"instagram_account_id": account.id},
            )

    @staticmethod
    def _require_token_manager(actor: Actor) -> None:
        if isinstance(actor, AgentActor):
            raise PermissionDeniedError("AI agents cannot manage OAuth tokens")
        if not isinstance(actor, HumanActor | SystemActor):
            raise PermissionDeniedError("Not allowed")
