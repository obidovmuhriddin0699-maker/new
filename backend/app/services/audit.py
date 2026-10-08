"""Audit logging service (append-only).

Records are written inside the caller's transaction, so a rolled-back
operation leaves no "success" audit row. Denied/failed attempts are recorded
with ``record_failure`` after the rollback so they are never lost.
Sensitive values are redacted recursively before storage.
"""

import re
from typing import Any

from sqlalchemy.orm import Session

from app.core.actors import Actor, HumanActor
from app.core.logging import request_id_var
from app.models import AuditLog, User
from app.models.enums import AuditAction
from app.repositories import AuditLogRepository

_SENSITIVE = re.compile(
    r"(password|passwd|secret|token|authorization|api[_-]?key|encryption[_-]?key|"
    r"private[_-]?key|fernet|credential|cookie)",
    re.IGNORECASE,
)
REDACTED = "***REDACTED***"


def sanitize(value: Any, _depth: int = 0) -> Any:
    if _depth > 8:
        return "…"
    if isinstance(value, dict):
        return {
            str(k): (REDACTED if _SENSITIVE.search(str(k)) else sanitize(v, _depth + 1))
            for k, v in value.items()
        }
    if isinstance(value, list | tuple | set):
        return [sanitize(v, _depth + 1) for v in value]
    if isinstance(value, str | int | float | bool) or value is None:
        if isinstance(value, str) and len(value) > 2000:
            return value[:2000] + "…"
        return value
    return str(value)


class AuditLogService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.repo = AuditLogRepository(session)

    def record(
        self,
        action: AuditAction,
        actor: Actor,
        *,
        content_id: int | None = None,
        content_version: int | None = None,
        status: str = "SUCCESS",
        error: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> AuditLog:
        details = dict(details or {})
        actor_user_id: int | None = None
        if isinstance(actor, HumanActor):
            if self.session.get(User, actor.user_id) is not None:
                actor_user_id = actor.user_id
            else:
                # Unverified/forged identity: keep the claim as data, not as a FK.
                details["claimed_user_id"] = actor.user_id
        entry = AuditLog(
            actor_type=actor.actor_type,
            actor_user_id=actor_user_id,
            actor_name=actor.display_name,
            action=action.value,
            content_id=content_id,
            content_version=content_version,
            status=status,
            error=error[:2000] if error else None,
            details=sanitize(details),
            request_id=request_id_var.get(),
        )
        return self.repo.add(entry)

    def record_failure(
        self,
        action: AuditAction,
        actor: Actor,
        *,
        error: str,
        content_id: int | None = None,
        content_version: int | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        """Persist a denied/failed attempt in its own transaction (after rollback)."""
        if self.session.info.get("atomic_depth", 0) > 0:
            # Inside a larger transaction: record there; the caller owns commit/rollback.
            self.record(
                action,
                actor,
                content_id=content_id,
                content_version=content_version,
                status="DENIED",
                error=error,
                details=details,
            )
            return
        self.session.rollback()
        self.record(
            action,
            actor,
            content_id=content_id,
            content_version=content_version,
            status="DENIED",
            error=error,
            details=details,
        )
        self.session.commit()
