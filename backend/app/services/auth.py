"""Authentication: login with brute-force protection, logout, session revocation,
password change. Every outcome is audited (never the password)."""

from datetime import UTC, datetime

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.core.actors import HumanActor, SystemActor
from app.core.errors import AppError, AuthenticationError
from app.core.ratelimit import (
    LOGIN_ACCOUNT_FAILURES,
    LOGIN_FAILURES,
    LOGIN_IP,
    RateLimitedError,
    get_limiter,
)
from app.core.security import create_access_token, hash_password, verify_password
from app.core.transaction import atomic
from app.models import RevokedToken, User
from app.models.base import utcnow
from app.models.enums import AuditAction
from app.services.audit import AuditLogService

AUTH_ACTOR = SystemActor("auth")
MIN_PASSWORD_LENGTH = 12
# Hash of a random secret keeps timing similar for unknown e-mails.
_DUMMY_HASH = hash_password("dummy-password-for-timing-only")


def validate_new_password(password: str, email: str) -> None:
    if len(password) < MIN_PASSWORD_LENGTH:
        raise AppError(
            f"Parol kamida {MIN_PASSWORD_LENGTH} belgidan iborat bo‘lishi kerak.",
            code="weak_password",
        )
    local = email.split("@", 1)[0].lower()
    if len(local) >= 4 and local in password.lower():
        raise AppError("Parolda e-mail nomi bo‘lmasligi kerak.", code="weak_password")
    if len(set(password)) < 5:
        raise AppError("Parol juda oddiy.", code="weak_password")


class AuthService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.audit = AuditLogService(session)
        self.limiter = get_limiter()

    # ------------------------------------------------------------------ login
    def login(self, email: str, password: str, *, ip: str) -> tuple[str, User]:
        email = email.lower()
        fail_key = f"{email}|{ip}"
        # Per-IP volume limit and per-(e-mail, IP) failure lockout, checked before any work.
        allowed, retry = self.limiter.hit(LOGIN_IP, ip)
        if allowed:
            allowed, retry = self.limiter.peek(LOGIN_FAILURES, fail_key)
        if allowed:
            allowed, retry = self.limiter.peek(LOGIN_ACCOUNT_FAILURES, email)
        if not allowed:
            self._audit_failure(AuditAction.AUTH_LOGIN_BLOCKED, email, ip, "rate limited")
            raise RateLimitedError(
                "Juda ko‘p urinish. Biroz kuting va qayta urinib ko‘ring.", retry
            )

        user = self.session.scalar(
            select(User).where(User.email == email, User.deleted_at.is_(None))
        )
        valid = verify_password(password, user.password_hash if user else _DUMMY_HASH)
        if user is None or not valid or not user.is_active:
            self.limiter.hit(LOGIN_FAILURES, fail_key)
            self.limiter.hit(LOGIN_ACCOUNT_FAILURES, email)
            reason = "unknown email" if user is None else ("inactive" if valid else "bad password")
            self._audit_failure(AuditAction.AUTH_LOGIN_FAILED, email, ip, reason, user)
            raise AuthenticationError("Invalid email or password")

        self.limiter.reset(LOGIN_FAILURES, fail_key)
        with atomic(self.session):
            user.last_login_at = utcnow()
            self.audit.record(
                AuditAction.AUTH_LOGIN_SUCCEEDED,
                HumanActor(user_id=user.id),
                details={"ip": ip},
            )
        return create_access_token(str(user.id), {"role": user.role.value}), user

    def _audit_failure(
        self, action: AuditAction, email: str, ip: str, reason: str, user: User | None = None
    ) -> None:
        with atomic(self.session):
            self.audit.record(
                action,
                AUTH_ACTOR,
                status="FAILED",
                error=reason,
                details={"email": email[:320], "ip": ip, "user_id": user.id if user else None},
            )

    # ------------------------------------------------------------------ sessions
    def logout(self, user: User, payload: dict) -> None:
        """Revoke this access token (by jti) until its natural expiry."""
        jti = payload.get("jti")
        with atomic(self.session):
            if jti and self.session.get(RevokedToken, jti) is None:
                self.session.add(
                    RevokedToken(
                        jti=str(jti)[:64],
                        user_id=user.id,
                        expires_at=datetime.fromtimestamp(int(payload["exp"]), UTC),
                    )
                )
            self.audit.record(AuditAction.AUTH_LOGOUT, HumanActor(user_id=user.id))
            # Housekeeping: expired entries are useless.
            self.session.execute(delete(RevokedToken).where(RevokedToken.expires_at < utcnow()))

    def revoke_all_sessions(self, user: User, *, reason: str = "logout_all") -> None:
        with atomic(self.session):
            user.sessions_valid_after = utcnow()
            self.audit.record(
                AuditAction.AUTH_SESSIONS_REVOKED,
                HumanActor(user_id=user.id),
                details={"reason": reason},
            )

    def change_password(self, user: User, current: str, new: str) -> None:
        if not verify_password(current, user.password_hash):
            self._audit_failure(
                AuditAction.AUTH_LOGIN_FAILED, user.email, "-", "password change: bad current", user
            )
            # 400, not 401: a typo must not end the session the user is typing in.
            raise AppError("Joriy parol noto‘g‘ri", code="invalid_current_password")
        validate_new_password(new, user.email)
        if verify_password(new, user.password_hash):
            raise AppError("Yangi parol eskisidan farq qilishi kerak.", code="weak_password")
        with atomic(self.session):
            user.password_hash = hash_password(new)
            user.password_changed_at = utcnow()
            # Every existing session (other devices, a stolen token) stops working.
            user.sessions_valid_after = utcnow()
            self.audit.record(AuditAction.AUTH_PASSWORD_CHANGED, HumanActor(user_id=user.id))

    # ------------------------------------------------------------------ token checks
    def is_revoked(self, user: User, payload: dict) -> bool:
        jti = payload.get("jti")
        if jti and self.session.get(RevokedToken, str(jti)) is not None:
            return True
        if user.sessions_valid_after is not None:
            issued_ms = int(payload.get("iat_ms") or int(payload.get("iat", 0)) * 1000)
            if issued_ms <= int(user.sessions_valid_after.timestamp() * 1000):
                return True
        return False
