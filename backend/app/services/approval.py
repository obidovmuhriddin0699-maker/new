"""Human approval decisions and publish authorization.

Rules enforced here:
* approve / reject / request-edit require a verified, active human approver;
  agents and system actors are refused (``ApprovalForbiddenError``);
* the human must state the version they reviewed (``expected_version``);
  a mismatch is refused, so content that changed meanwhile cannot be approved;
* an approval binds to (content_id, version, content_hash);
* ``require_valid_approval`` is the only way to obtain publish authorization
  and re-checks version, hash, invalidation and the approver's status.
"""

from dataclasses import dataclass
from typing import cast

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.actors import Actor, HumanActor
from app.core.errors import (
    AppError,
    ApprovalRequiredError,
    NotFoundError,
    VersionMismatchError,
)
from app.core.transaction import atomic
from app.models import Approval, Content
from app.models.enums import (
    ApprovalDecision,
    AuditAction,
    ContentStatus,
)
from app.repositories import (
    ApprovalRepository,
    ContentAssetRepository,
    ContentRepository,
    ContentVersionRepository,
    UserRepository,
)
from app.services.audit import AuditLogService
from app.services.content_hash import compute_hash, content_snapshot, media_snapshot
from app.services.content_state import apply_transition, assert_transition
from app.services.guards import APPROVER_ROLES, require_human_approver
from app.services.invalidation import cancel_pending_schedules, invalidate_active_approvals


@dataclass(frozen=True, slots=True)
class ApprovalResult:
    approval: Approval
    content: Content
    created: bool  # False when an identical approval already existed (idempotent replay)


class ApprovalService:
    def __init__(self, session: Session, audit: AuditLogService | None = None) -> None:
        self.session = session
        self.audit = audit or AuditLogService(session)
        self.contents = ContentRepository(session)
        self.approvals = ApprovalRepository(session)
        self.versions = ContentVersionRepository(session)
        self.assets = ContentAssetRepository(session)

    # ------------------------------------------------------------------ decisions
    def approve(
        self, content_id: int, actor: Actor, *, expected_version: int, comment: str | None = None
    ) -> ApprovalResult:
        try:
            with atomic(self.session):
                require_human_approver(self.session, actor)
                human = cast(HumanActor, actor)  # verified by the guard above
                content = self._load(content_id)
                self._check_version(content, expected_version)

                existing = self.approvals.get_active_approval(content.id, content.version)
                if existing is not None and content.status in (
                    ContentStatus.APPROVED,
                    ContentStatus.SCHEDULED,
                ):
                    return ApprovalResult(existing, content, created=False)

                assert_transition(content.status, ContentStatus.APPROVED)
                content_hash = self._verified_hash(content)
                approval = Approval(
                    content_id=content.id,
                    content_version=content.version,
                    content_hash=content_hash,
                    decision=ApprovalDecision.APPROVED,
                    decided_by_user_id=human.user_id,
                    channel=human.channel,
                    comment=comment,
                )
                self.approvals.add(approval)
                apply_transition(content, ContentStatus.APPROVED)
                self.audit.record(
                    AuditAction.CONTENT_APPROVED,
                    actor,
                    content_id=content.id,
                    content_version=content.version,
                    details={
                        "approval_id": approval.id,
                        "channel": human.channel.value,
                        "content_hash": content_hash,
                    },
                )
                return ApprovalResult(approval, content, created=True)
        except IntegrityError:
            # Concurrent approve of the same version: the partial unique index won.
            existing = self.approvals.get_active_approval(content_id, expected_version)
            content = self.contents.get(content_id)
            if existing is None or content is None:
                raise
            return ApprovalResult(existing, content, created=False)
        except AppError as exc:
            self._record_denial(AuditAction.CONTENT_APPROVED, actor, content_id, exc)
            raise

    def reject(
        self, content_id: int, actor: Actor, *, expected_version: int, comment: str | None = None
    ) -> Content:
        return self._decide(
            content_id,
            actor,
            expected_version,
            comment,
            decision=ApprovalDecision.REJECTED,
            target=ContentStatus.REJECTED,
            action=AuditAction.CONTENT_REJECTED,
        )

    def request_edit(
        self, content_id: int, actor: Actor, *, expected_version: int, comment: str | None = None
    ) -> Content:
        return self._decide(
            content_id,
            actor,
            expected_version,
            comment,
            decision=ApprovalDecision.EDIT_REQUESTED,
            target=ContentStatus.EDIT_REQUESTED,
            action=AuditAction.CONTENT_EDIT_REQUESTED,
        )

    # ------------------------------------------------------------ authorization
    def get_valid_approval(self, content: Content) -> Approval | None:
        """Active approval that authorises publishing *this exact* content, else None."""
        approval = self.approvals.get_active_approval(content.id, content.version)
        if approval is None or approval.content_version != content.version:
            return None
        version_row = self.versions.get_version(content.id, content.version)
        if version_row is None or version_row.content_hash != approval.content_hash:
            return None
        if self._current_hash(content) != approval.content_hash:
            return None
        approver = UserRepository(self.session).get_active(approval.decided_by_user_id)
        if approver is None or approver.role not in APPROVER_ROLES:
            return None
        return approval

    def require_valid_approval(self, content: Content) -> Approval:
        approval = self.get_valid_approval(content)
        if approval is None:
            raise ApprovalRequiredError(
                "A human approval of the current content version is required",
                details={"content_id": content.id, "version": content.version},
            )
        return approval

    # ------------------------------------------------------------------ helpers
    def _decide(
        self,
        content_id: int,
        actor: Actor,
        expected_version: int,
        comment: str | None,
        *,
        decision: ApprovalDecision,
        target: ContentStatus,
        action: AuditAction,
    ) -> Content:
        try:
            with atomic(self.session):
                require_human_approver(self.session, actor)
                human = cast(HumanActor, actor)  # verified by the guard above
                content = self._load(content_id)
                self._check_version(content, expected_version)
                assert_transition(content.status, target)
                content_hash = self._current_hash(content)
                self.approvals.add(
                    Approval(
                        content_id=content.id,
                        content_version=content.version,
                        content_hash=content_hash,
                        decision=decision,
                        decided_by_user_id=human.user_id,
                        channel=human.channel,
                        comment=comment,
                    )
                )
                invalidate_active_approvals(
                    self.session, self.audit, content, actor, reason=decision.value.lower()
                )
                cancel_pending_schedules(
                    self.session, self.audit, content, actor, reason=decision.value.lower()
                )
                apply_transition(content, target)
                self.audit.record(
                    action,
                    actor,
                    content_id=content.id,
                    content_version=content.version,
                    details={"channel": human.channel.value, "comment": comment},
                )
                return content
        except AppError as exc:
            self._record_denial(action, actor, content_id, exc)
            raise

    def _load(self, content_id: int) -> Content:
        content = self.contents.get_for_update(content_id)
        if content is None:
            raise NotFoundError("Content not found")
        return content

    @staticmethod
    def _check_version(content: Content, expected_version: int) -> None:
        if content.version != expected_version:
            raise VersionMismatchError(
                "Content changed since you reviewed it; reload and review the latest version",
                details={"expected_version": expected_version, "current_version": content.version},
            )

    def _current_hash(self, content: Content) -> str:
        media = media_snapshot(self.assets.list_for_content(content.id))
        return compute_hash(content_snapshot(content, media))

    def _verified_hash(self, content: Content) -> str:
        """Hash of the working copy; must match the stored snapshot of this version."""
        current = self._current_hash(content)
        version_row = self.versions.get_version(content.id, content.version)
        if version_row is None or version_row.content_hash != current:
            raise ApprovalRequiredError(
                "Content does not match its recorded version; it must be re-versioned",
                code="content_integrity_error",
            )
        return current

    def _record_denial(
        self, action: AuditAction, actor: Actor, content_id: int, exc: AppError
    ) -> None:
        if isinstance(exc, NotFoundError):
            return
        content = self.contents.get(content_id)
        self.audit.record_failure(
            AuditAction.APPROVAL_DENIED,
            actor,
            error=exc.message,
            content_id=content_id if content is not None else None,
            content_version=content.version if content is not None else None,
            details={"attempted_action": action.value, "code": exc.code},
        )
