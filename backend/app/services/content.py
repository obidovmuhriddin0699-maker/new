"""Content lifecycle: create, edit (versioned), review submission, generation
hooks for agents, and publish-state transitions for the publish service.

No method here can publish to Instagram. ``start_publishing`` only moves an
approved version into PUBLISHING and may only be called by the backend
publish service (PHASE 8); agents are refused.
"""

from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Any

from sqlalchemy.orm import Session

from app.agents.permissions import AgentTool
from app.core.actors import Actor, AgentActor, HumanActor
from app.core.errors import (
    AppError,
    ConflictError,
    InvalidStateTransitionError,
    NotFoundError,
    PermissionDeniedError,
    VersionMismatchError,
)
from app.core.transaction import atomic
from app.models import Approval, AuditLog, Content, ContentAsset, ContentVersion
from app.models.base import utcnow
from app.models.enums import (
    ActorType,
    AssetKind,
    AuditAction,
    ContentLanguage,
    ContentStatus,
    ContentType,
    ScheduleStatus,
)
from app.providers.media import DEFAULT_ASPECT_RATIO
from app.repositories import (
    ApprovalRepository,
    AuditLogRepository,
    ContentAssetRepository,
    ContentRepository,
    ContentScheduleRepository,
    ContentVersionRepository,
)
from app.services.approval import ApprovalService
from app.services.audit import AuditLogService
from app.services.content_hash import (
    VERSIONED_FIELDS,
    compute_hash,
    content_snapshot,
    media_snapshot,
)
from app.services.content_state import (
    EDITABLE_STATES,
    STATUS_AFTER_EDIT,
    apply_transition,
    assert_transition,
)
from app.services.guards import require_human_writer, require_publish_service, require_writer
from app.services.invalidation import cancel_pending_schedules, invalidate_active_approvals

EDITABLE_FIELDS: frozenset[str] = frozenset(VERSIONED_FIELDS) | {
    "brand_profile_id",
    "instagram_account_id",
    "planned_date",
}


@dataclass(slots=True)
class ContentHistory:
    content: Content
    versions: Sequence[ContentVersion]
    approvals: Sequence[Approval]
    events: Sequence[AuditLog]


@dataclass(slots=True)
class AssetInput:
    kind: AssetKind
    position: int = 0
    storage_path: str | None = None
    public_url: str | None = None
    mime_type: str | None = None
    width: int | None = None
    height: int | None = None
    duration_seconds: float | None = None
    checksum_sha256: str | None = None
    generation_prompt: str | None = None
    provider: str | None = None
    extra: dict[str, Any] = field(default_factory=dict)


class ContentService:
    def __init__(self, session: Session, audit: AuditLogService | None = None) -> None:
        self.session = session
        self.audit = audit or AuditLogService(session)
        self.contents = ContentRepository(session)
        self.versions = ContentVersionRepository(session)
        self.assets = ContentAssetRepository(session)
        self.schedules = ContentScheduleRepository(session)
        self.approval_service = ApprovalService(session, self.audit)

    # ------------------------------------------------------------------ reads
    def get(self, content_id: int) -> Content:
        content = self.contents.get(content_id)
        if content is None:
            raise NotFoundError("Content not found")
        return content

    def list(
        self,
        *,
        status: ContentStatus | None = None,
        content_type: ContentType | None = None,
        offset: int = 0,
        limit: int = 50,
        sort: str = "newest",
    ) -> tuple[Sequence[Content], int]:
        return self.contents.search(
            status=status, content_type=content_type, offset=offset, limit=limit, sort=sort
        )

    def list_assets(self, content_id: int) -> Sequence[ContentAsset]:
        return self.assets.list_for_content(content_id)

    def history(self, content_id: int) -> ContentHistory:
        content = self.get(content_id)
        return ContentHistory(
            content=content,
            versions=self.versions.list_for_content(content_id),
            approvals=ApprovalRepository(self.session).list_for_content(content_id),
            events=AuditLogRepository(self.session).list_for_content(content_id),
        )

    def is_publish_authorized(self, content: Content) -> bool:
        return self.approval_service.get_valid_approval(content) is not None

    # ------------------------------------------------------------------ create / edit
    def create(
        self,
        actor: Actor,
        *,
        content_type: ContentType,
        language: ContentLanguage = ContentLanguage.UZ,
        ai_metadata: dict[str, Any] | None = None,
        change_note: str | None = None,
        **fields: Any,
    ) -> Content:
        with atomic(self.session):
            require_writer(self.session, actor, AgentTool.CREATE_CONTENT)
            self._reject_unknown_fields(fields)
            if fields.get("aspect_ratio") is None:
                # Publishing requires a format; hand-made content gets the type's default
                # (as AI drafts do) instead of a blocker the editor cannot see a cause for.
                fields["aspect_ratio"] = DEFAULT_ASPECT_RATIO[content_type]
            content = Content(
                content_type=content_type,
                language=language,
                status=ContentStatus.DRAFT,
                version=1,
                created_by=actor.actor_type,
                hashtags=[],
                structure={},
            )
            for name, value in fields.items():
                setattr(content, name, value)
            self.contents.add(content)
            version = self._snapshot_version(content, actor, ai_metadata, change_note or "created")
            self.audit.record(
                AuditAction.CONTENT_CREATED,
                actor,
                content_id=content.id,
                content_version=1,
                details={"content_type": content_type.value, "language": language.value},
            )
            self._audit_version(actor, content, version)
            return content

    def update(
        self,
        content_id: int,
        actor: Actor,
        *,
        expected_version: int,
        changes: dict[str, Any],
        change_note: str | None = None,
        ai_metadata: dict[str, Any] | None = None,
    ) -> Content:
        """Edit content. Any effective change creates a new immutable version and
        invalidates approvals of earlier versions."""
        with atomic(self.session):
            require_writer(self.session, actor, AgentTool.EDIT_CONTENT)
            self._reject_unknown_fields(changes)
            content = self._load_for_update(content_id)
            self._check_version(content, expected_version)
            if content.status not in EDITABLE_STATES:
                raise InvalidStateTransitionError(
                    f"Content in status {content.status.value} cannot be edited",
                    details={"status": content.status.value},
                )
            if isinstance(actor, AgentActor) and content.status in STATUS_AFTER_EDIT:
                # Agents may not touch human-approved (or failed-publish) content.
                raise PermissionDeniedError("Agents cannot edit approved or scheduled content")

            changed = {k: v for k, v in changes.items() if getattr(content, k) != v}
            if not changed:
                return content
            before = {k: _jsonable(getattr(content, k)) for k in changed}
            for name, value in changed.items():
                setattr(content, name, value)

            # The target account is part of what a human approved: moving approved
            # content to another account needs a new version and a new approval.
            versioned_change = any(
                k in VERSIONED_FIELDS or k == "instagram_account_id" for k in changed
            )
            self.audit.record(
                AuditAction.CONTENT_UPDATED,
                actor,
                content_id=content.id,
                content_version=content.version,
                details={
                    "fields": sorted(changed),
                    "before": before,
                    "after": {k: _jsonable(v) for k, v in changed.items()},
                },
            )
            if versioned_change:
                self._new_version(content, actor, ai_metadata, change_note or "edited")
            return content

    def add_asset(
        self, content_id: int, actor: Actor, *, expected_version: int, asset: AssetInput
    ) -> ContentAsset:
        with atomic(self.session):
            require_writer(self.session, actor, AgentTool.GENERATE_MEDIA)
            content = self._load_for_update(content_id)
            self._check_version(content, expected_version)
            self._require_editable(content, actor)
            row = ContentAsset(
                content_id=content.id,
                kind=asset.kind,
                position=asset.position,
                storage_path=asset.storage_path,
                public_url=asset.public_url,
                mime_type=asset.mime_type,
                width=asset.width,
                height=asset.height,
                duration_seconds=asset.duration_seconds,
                checksum_sha256=asset.checksum_sha256,
                generation_prompt=asset.generation_prompt,
                provider=asset.provider,
            )
            self.assets.add(row)
            self.session.refresh(content, ["assets"])
            self.audit.record(
                AuditAction.ASSET_ADDED,
                actor,
                content_id=content.id,
                content_version=content.version,
                details={"asset_id": row.id, "kind": asset.kind.value, "position": asset.position},
            )
            self._new_version(content, actor, None, f"asset {row.id} added")
            return row

    def remove_asset(
        self, content_id: int, asset_id: int, actor: Actor, *, expected_version: int
    ) -> Content:
        with atomic(self.session):
            require_writer(self.session, actor, AgentTool.GENERATE_MEDIA)
            content = self._load_for_update(content_id)
            self._check_version(content, expected_version)
            self._require_editable(content, actor)
            asset = self.assets.get(asset_id)
            if asset is None or asset.content_id != content.id:
                raise NotFoundError("Asset not found")
            self.assets.soft_delete(asset)
            self.audit.record(
                AuditAction.ASSET_REMOVED,
                actor,
                content_id=content.id,
                content_version=content.version,
                details={"asset_id": asset_id},
            )
            self._new_version(content, actor, None, f"asset {asset_id} removed")
            return content

    def soft_delete(self, content_id: int, actor: Actor) -> None:
        with atomic(self.session):
            require_human_writer(self.session, actor)
            content = self._load_for_update(content_id)
            if content.status == ContentStatus.PUBLISHING:
                raise ConflictError("Content is being published and cannot be deleted")
            invalidate_active_approvals(self.session, self.audit, content, actor, "deleted")
            cancel_pending_schedules(self.session, self.audit, content, actor, "deleted")
            self.contents.soft_delete(content)
            self.audit.record(
                AuditAction.CONTENT_DELETED,
                actor,
                content_id=content.id,
                content_version=content.version,
            )

    # ------------------------------------------------------------------ review
    def submit_for_review(self, content_id: int, actor: Actor) -> Content:
        with atomic(self.session):
            require_writer(self.session, actor, AgentTool.REQUEST_APPROVAL)
            content = self._load_for_update(content_id)
            assert_transition(content.status, ContentStatus.READY_FOR_REVIEW)
            if content.status not in (ContentStatus.DRAFT, ContentStatus.EDIT_REQUESTED):
                raise InvalidStateTransitionError(
                    "Only DRAFT or EDIT_REQUESTED content can be submitted for review"
                )
            if not (content.caption or content.script):
                raise ConflictError(
                    "Content needs a caption or script before review", code="content_incomplete"
                )
            apply_transition(content, ContentStatus.READY_FOR_REVIEW)
            self.audit.record(
                AuditAction.CONTENT_SUBMITTED_FOR_REVIEW,
                actor,
                content_id=content.id,
                content_version=content.version,
            )
            return content

    # ------------------------------------------------------------------ AI generation hooks
    def start_generation(self, content_id: int, actor: AgentActor) -> Content:
        with atomic(self.session):
            self._require_agent(actor, AgentTool.CREATE_CONTENT)
            content = self._load_for_update(content_id)
            apply_transition(content, ContentStatus.GENERATING)
            self.audit.record(
                AuditAction.CONTENT_GENERATION_STARTED,
                actor,
                content_id=content.id,
                content_version=content.version,
            )
            return content

    def complete_generation(
        self,
        content_id: int,
        actor: AgentActor,
        *,
        fields: dict[str, Any],
        ai_metadata: dict[str, Any],
    ) -> Content:
        """Agent output becomes a new version and goes to human review — never further."""
        with atomic(self.session):
            self._require_agent(actor, AgentTool.EDIT_CONTENT)
            self._reject_unknown_fields(fields)
            content = self._load_for_update(content_id)
            if content.status != ContentStatus.GENERATING:
                raise InvalidStateTransitionError("Content is not being generated")
            for name, value in fields.items():
                setattr(content, name, value)
            self._new_version(content, actor, ai_metadata, "AI generation")
            apply_transition(content, ContentStatus.READY_FOR_REVIEW)
            self.audit.record(
                AuditAction.CONTENT_SUBMITTED_FOR_REVIEW,
                actor,
                content_id=content.id,
                content_version=content.version,
            )
            return content

    def fail_generation(self, content_id: int, actor: AgentActor, *, error: str) -> Content:
        with atomic(self.session):
            self._require_agent(actor, AgentTool.CREATE_CONTENT)
            content = self._load_for_update(content_id)
            apply_transition(content, ContentStatus.FAILED)
            content.last_error = error[:2000]
            self.audit.record(
                AuditAction.CONTENT_GENERATION_FAILED,
                actor,
                content_id=content.id,
                content_version=content.version,
                status="FAILED",
                error=error,
            )
            return content

    # ------------------------------------------------------------------ publish states (PHASE 8)
    def start_publishing(
        self, content_id: int, actor: Actor, *, from_schedule: bool = False
    ) -> Approval:
        """Move an approved version into PUBLISHING. Does NOT contact Instagram.

        Refused unless: actor is the backend publish service; the transition is
        allowed; an active human approval exists for the current version with a
        matching hash; and the version has not already been published.
        """
        try:
            with atomic(self.session):
                require_publish_service(actor)
                content = self._load_for_update(content_id)
                if from_schedule and content.status == ContentStatus.APPROVED:
                    # The worker runs a schedule, so the content is SCHEDULED (or FAILED
                    # for a retry). APPROVED means it was unscheduled after the worker
                    # claimed it: the human cancelled, so do not publish. Checked under
                    # the row lock that unschedule() also takes.
                    raise ConflictError("Publishing was cancelled", code="publish_cancelled")
                assert_transition(content.status, ContentStatus.PUBLISHING)
                approval = self.approval_service.require_valid_approval(content)
                for schedule in self.schedules.list_for_content(content.id):
                    if (
                        schedule.content_version == content.version
                        and schedule.status == ScheduleStatus.DONE
                    ):
                        raise ConflictError(
                            "This version was already published", code="already_published"
                        )
                apply_transition(content, ContentStatus.PUBLISHING)
                self.audit.record(
                    AuditAction.CONTENT_PUBLISH_STARTED,
                    actor,
                    content_id=content.id,
                    content_version=content.version,
                    details={
                        "approval_id": approval.id,
                        "approved_by_user_id": approval.decided_by_user_id,
                    },
                )
                return approval
        except AppError as exc:
            if not isinstance(exc, NotFoundError):
                current = self.contents.get(content_id)
                self.audit.record_failure(
                    AuditAction.STATE_TRANSITION_DENIED,
                    actor,
                    error=exc.message,
                    content_id=content_id if current else None,
                    content_version=current.version if current else None,
                    details={"attempted_action": "start_publishing", "code": exc.code},
                )
            raise

    def mark_published(
        self,
        content_id: int,
        actor: Actor,
        *,
        ig_media_id: str | None,
        permalink: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> Content:
        with atomic(self.session):
            require_publish_service(actor)
            content = self._load_for_update(content_id)
            apply_transition(content, ContentStatus.PUBLISHED)
            content.ig_media_id = ig_media_id
            content.ig_permalink = permalink
            content.published_at = utcnow()
            content.last_error = None
            for schedule in self.schedules.list_for_content(content.id):
                if schedule.content_version == content.version and schedule.status in (
                    ScheduleStatus.PENDING,
                    ScheduleStatus.PROCESSING,
                ):
                    schedule.status = ScheduleStatus.DONE
            self.audit.record(
                AuditAction.CONTENT_PUBLISH_SUCCEEDED,
                actor,
                content_id=content.id,
                content_version=content.version,
                details={**(details or {}), "ig_media_id": ig_media_id, "permalink": permalink},
            )
            return content

    def mark_publish_failed(self, content_id: int, actor: Actor, *, error: str) -> Content:
        with atomic(self.session):
            require_publish_service(actor)
            content = self._load_for_update(content_id)
            apply_transition(content, ContentStatus.FAILED)
            content.last_error = error[:2000]
            self.audit.record(
                AuditAction.CONTENT_PUBLISH_FAILED,
                actor,
                content_id=content.id,
                content_version=content.version,
                status="FAILED",
                error=error,
            )
            return content

    # ------------------------------------------------------------------ internals
    def _load_for_update(self, content_id: int) -> Content:
        content = self.contents.get_for_update(content_id)
        if content is None:
            raise NotFoundError("Content not found")
        return content

    @staticmethod
    def _check_version(content: Content, expected_version: int) -> None:
        if content.version != expected_version:
            raise VersionMismatchError(
                "Content was changed by someone else; reload and try again",
                details={"expected_version": expected_version, "current_version": content.version},
            )

    def _require_editable(self, content: Content, actor: Actor) -> None:
        if content.status not in EDITABLE_STATES:
            raise InvalidStateTransitionError(
                f"Content in status {content.status.value} cannot be edited"
            )
        if isinstance(actor, AgentActor) and content.status in STATUS_AFTER_EDIT:
            raise PermissionDeniedError("Agents cannot edit approved or scheduled content")

    @staticmethod
    def _require_agent(actor: Actor, tool: AgentTool) -> None:
        if not isinstance(actor, AgentActor):
            raise PermissionDeniedError("Only AI agents run generation")
        if tool not in actor.tools:
            raise PermissionDeniedError(f"Agent '{actor.name}' lacks {tool.value}")

    @staticmethod
    def _reject_unknown_fields(fields: dict[str, Any]) -> None:
        unknown = set(fields) - EDITABLE_FIELDS
        if unknown:
            raise AppError(f"Unknown or read-only fields: {sorted(unknown)}", code="invalid_fields")

    def _snapshot_version(
        self,
        content: Content,
        actor: Actor,
        ai_metadata: dict[str, Any] | None,
        change_note: str | None,
    ) -> ContentVersion:
        media = media_snapshot(self.assets.list_for_content(content.id))
        snapshot = content_snapshot(content, media)
        version = ContentVersion(
            content_id=content.id,
            version=content.version,
            content_type=content.content_type,
            language=content.language,
            topic=content.topic,
            hook=content.hook,
            caption=content.caption,
            hashtags=list(content.hashtags or []),
            cta=content.cta,
            script=content.script,
            visual_prompt=content.visual_prompt,
            aspect_ratio=content.aspect_ratio,
            structure=dict(content.structure or {}),
            media=media,
            ai_metadata=ai_metadata or {},
            source=actor.actor_type,
            created_by_user_id=actor.user_id if isinstance(actor, HumanActor) else None,
            created_by_name=actor.display_name,
            change_note=change_note,
            content_hash=compute_hash(snapshot),
        )
        return self.versions.add(version)

    def _new_version(
        self,
        content: Content,
        actor: Actor,
        ai_metadata: dict[str, Any] | None,
        change_note: str | None,
    ) -> ContentVersion:
        previous_status = content.status
        content.version += 1
        if actor.actor_type == ActorType.AGENT:
            content.created_by = ActorType.AGENT
        version = self._snapshot_version(content, actor, ai_metadata, change_note)
        invalidate_active_approvals(
            self.session, self.audit, content, actor, reason=f"content changed (v{content.version})"
        )
        cancel_pending_schedules(
            self.session, self.audit, content, actor, reason=f"content changed (v{content.version})"
        )
        if previous_status in STATUS_AFTER_EDIT:
            apply_transition(content, STATUS_AFTER_EDIT[previous_status])
        self._audit_version(actor, content, version)
        return version

    def _audit_version(self, actor: Actor, content: Content, version: ContentVersion) -> None:
        self.audit.record(
            AuditAction.CONTENT_VERSION_CREATED,
            actor,
            content_id=content.id,
            content_version=version.version,
            details={"content_hash": version.content_hash, "change_note": version.change_note},
        )


def _jsonable(value: Any) -> Any:
    if hasattr(value, "value"):
        return value.value
    if isinstance(value, list):
        return list(value)
    return value
