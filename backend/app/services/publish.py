"""Publishing to Instagram — the only code path that ever calls ``media_publish``.

    USER → APPROVE → SYSTEM (this service) → META API → INSTAGRAM

* A human OWNER/ADMIN requests a publish (now) or schedules it; AI never can.
* Before anything is sent to Meta: the human approval of the *current* version is
  re-verified (hash, approver, expiry) and the readiness preflight must pass.
* What is published is the approved version's snapshot (text + media URLs).
* Duplicate prevention:
  - one ``ContentSchedule`` per (content, version) via the idempotency key;
  - a worker must *claim* a schedule (PENDING → PROCESSING) before working on it;
  - the container id is committed before ``media_publish`` is called, and retries
    reuse it. Meta publishes a container at most once;
  - if ``media_publish`` gets no answer, the outcome is *unknown*: the schedule is
    flagged and only the container's ``status_code`` decides (PUBLISHED → success,
    EXPIRED/ERROR → never published). Nothing is re-created blindly.
* ``META_DRY_RUN=true``: everything is checked and the exact plan is returned, but no
  request is sent to Meta and no state changes.
* Every step is audited, including who approved and who requested the publish.
"""

import logging
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import timedelta
from typing import Any, Literal

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.agents.structured import run_sync
from app.core.actors import PUBLISH_SERVICE_NAME, Actor, SystemActor
from app.core.caption import published_caption
from app.core.config import get_settings
from app.core.crypto import DecryptionError
from app.core.errors import AppError, ConflictError, NotFoundError, VersionMismatchError
from app.core.transaction import atomic
from app.integrations.meta.errors import MetaApiError, MetaErrorKind
from app.integrations.meta.publishing import (
    ContainerStatus,
    InstagramPublishingClient,
    PublishingLimit,
    PublishOutcomeUnknownError,
)
from app.models import Content, ContentSchedule, ContentVersion, InstagramAccount
from app.models.base import utcnow
from app.models.enums import AuditAction, ContentStatus, ContentType, ScheduleStatus
from app.repositories import (
    ContentRepository,
    ContentScheduleRepository,
    ContentVersionRepository,
)
from app.services.approval import ApprovalService
from app.services.audit import AuditLogService
from app.services.content import ContentService
from app.services.content_state import apply_transition, assert_transition
from app.services.guards import require_human_approver
from app.services.instagram import InstagramAccountService
from app.services.invalidation import invalidate_active_approvals
from app.services.review import Readiness, ReviewService
from app.services.schedule import publish_idempotency_key

logger = logging.getLogger(__name__)

PUBLISH_ACTOR = SystemActor(PUBLISH_SERVICE_NAME)
RETRYABLE = frozenset({MetaErrorKind.TRANSIENT, MetaErrorKind.NETWORK, MetaErrorKind.RATE_LIMIT})
CONTAINER_TTL = timedelta(hours=24)

ResultStatus = Literal[
    "dry_run", "queued", "published", "failed", "deferred", "in_progress", "skipped"
]
ClientFactory = Callable[[str, str], InstagramPublishingClient]


@dataclass(slots=True)
class PublishStep:
    endpoint: str
    params: dict[str, str]
    note: str = ""


@dataclass(slots=True)
class PublishPlan:
    content_id: int
    version: int
    content_type: ContentType
    caption: str
    items: list[dict[str, str]]  # per media item: container params (no tokens)
    final: dict[str, str] | None  # carousel container params (children filled at run time)
    account_id: int | None = None
    account_username: str | None = None

    def steps(self) -> list[PublishStep]:
        steps = [
            PublishStep("POST /{ig-user-id}/media", p, "carousel element" if self.final else "")
            for p in self.items
        ]
        if self.final is not None:
            steps.append(
                PublishStep(
                    "POST /{ig-user-id}/media",
                    {**self.final, "children": "<element container ids>"},
                    "carousel container",
                )
            )
        steps.append(PublishStep("GET /{container-id}?fields=status_code", {}, "wait for FINISHED"))
        steps.append(
            PublishStep("POST /{ig-user-id}/media_publish", {"creation_id": "<container id>"})
        )
        return steps


@dataclass(slots=True)
class PublishPreview:
    readiness: Readiness
    plan: PublishPlan | None
    dry_run: bool
    problems: list[str] = field(default_factory=list)


@dataclass(slots=True)
class PublishResult:
    status: ResultStatus
    content: Content | None
    schedule: ContentSchedule | None = None
    message: str = ""
    preview: PublishPreview | None = None


def build_plan(version: ContentVersion) -> PublishPlan:
    """Container parameters for the approved snapshot (pure; no I/O)."""
    media = sorted(
        [m for m in (version.media or []) if m.get("public_url")],
        key=lambda m: (m.get("position") or 0, m.get("asset_id") or 0),
    )
    is_story = version.content_type == ContentType.STORY
    caption = published_caption(
        hook=version.hook,
        caption=version.caption,
        cta=version.cta,
        hashtags=list(version.hashtags or []),
        is_story=is_story,
    )

    def media_param(m: dict[str, Any]) -> dict[str, str]:
        key = "video_url" if m.get("kind") == "VIDEO" else "image_url"
        return {key: str(m["public_url"])}

    items: list[dict[str, str]] = []
    final: dict[str, str] | None = None
    ct = version.content_type
    if ct == ContentType.CAROUSEL:
        for m in media:
            p = {**media_param(m), "is_carousel_item": "true"}
            if m.get("kind") == "VIDEO":
                p["media_type"] = "VIDEO"
            items.append(p)
        final = {"media_type": "CAROUSEL", "caption": caption}
    elif media:
        first = media[0]
        if ct == ContentType.REELS:
            items.append(
                {
                    "media_type": "REELS",
                    **media_param(first),
                    "caption": caption,
                    "share_to_feed": "true",
                }
            )
        elif ct == ContentType.STORY:
            items.append({"media_type": "STORIES", **media_param(first)})
        else:
            items.append({**media_param(first), "caption": caption})
    return PublishPlan(version.content_id, version.version, ct, caption, items, final)


class PublishService:
    def __init__(
        self,
        session: Session,
        client_factory: ClientFactory | None = None,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        self.session = session
        self.settings = get_settings()
        self.audit = AuditLogService(session)
        self.contents = ContentRepository(session)
        self.schedules = ContentScheduleRepository(session)
        self.versions = ContentVersionRepository(session)
        self.approvals = ApprovalService(session, self.audit)
        self.content_service = ContentService(session)
        self.review = ReviewService(session)
        self.client_factory: ClientFactory = client_factory or (
            lambda token, ig_user_id: InstagramPublishingClient(token, ig_user_id, self.settings)
        )
        self._sleep = sleep

    # ================================================================== preview
    def preview(self, content_id: int) -> PublishPreview:
        content = self._content(content_id)
        readiness = self.review.readiness(content.id)
        version = self.versions.get_version(content.id, content.version)
        plan = build_plan(version) if version else None
        account = self.review.publish_account(content)
        if plan and account:
            plan.account_id, plan.account_username = account.id, account.username
        problems = [c.message for c in readiness.checks if c.severity == "blocker" and not c.ok]
        return PublishPreview(readiness, plan, self.settings.meta_dry_run, problems)

    # ================================================================== request (human)
    def request_publish(
        self, content_id: int, actor: Actor, *, expected_version: int
    ) -> PublishResult:
        """Publish the current approved version now. Human OWNER/ADMIN only."""
        try:
            user = require_human_approver(self.session, actor)
        except AppError as exc:
            self.audit.record_failure(
                AuditAction.STATE_TRANSITION_DENIED,
                actor,
                error=exc.message,
                content_id=content_id if self.contents.get(content_id) else None,
                details={"attempted_action": "publish", "code": exc.code},
            )
            raise
        content = self._content(content_id)
        if content.version != expected_version:
            raise VersionMismatchError(
                "Content was changed by someone else; reload and try again",
                details={"expected_version": expected_version, "current_version": content.version},
            )

        if self.settings.meta_dry_run:
            preview = self.preview(content.id)
            with atomic(self.session):
                self.audit.record(
                    AuditAction.CONTENT_PUBLISH_DRY_RUN,
                    actor,
                    content_id=content.id,
                    content_version=content.version,
                    details={
                        "ready": preview.readiness.ready,
                        "problems": preview.problems[:10],
                        "steps": len(preview.plan.steps()) if preview.plan else 0,
                    },
                )
            return PublishResult(
                "dry_run",
                content,
                None,
                "DRY RUN: hech narsa Instagram’ga yuborilmadi (META_DRY_RUN=true).",
                preview,
            )

        with atomic(self.session):
            content = self.contents.get_for_update(content_id) or content
            if content.version != expected_version:
                raise ConflictError("Content changed; reload", code="version_mismatch")
            if content.status == ContentStatus.PUBLISHED:
                raise ConflictError("This version was already published", code="already_published")
            if content.status == ContentStatus.PUBLISHING:
                raise ConflictError("Publishing is already in progress", code="publish_in_progress")
            approval = self.approvals.require_valid_approval(content)
            key = publish_idempotency_key(content.id, content.version)
            schedule = self.schedules.get_by_idempotency_key(key)
            now = utcnow()
            if schedule is not None:
                if schedule.status == ScheduleStatus.DONE:
                    raise ConflictError(
                        "This version was already published", code="already_published"
                    )
                if schedule.status == ScheduleStatus.PROCESSING:
                    raise ConflictError(
                        "Publishing is already in progress", code="publish_in_progress"
                    )
                schedule.status = ScheduleStatus.PENDING
                schedule.scheduled_at = now
                schedule.approval_id = approval.id
                schedule.last_error = None
            else:
                if content.status == ContentStatus.APPROVED:
                    apply_transition(content, ContentStatus.SCHEDULED)
                elif content.status != ContentStatus.FAILED:
                    assert_transition(content.status, ContentStatus.PUBLISHING)
                schedule = self.schedules.add(
                    ContentSchedule(
                        content_id=content.id,
                        content_version=content.version,
                        approval_id=approval.id,
                        created_by_user_id=user.id,
                        scheduled_at=now,
                        status=ScheduleStatus.PENDING,
                        idempotency_key=key,
                    )
                )
            self.audit.record(
                AuditAction.CONTENT_PUBLISH_REQUESTED,
                actor,
                content_id=content.id,
                content_version=content.version,
                details={
                    "schedule_id": schedule.id,
                    "approval_id": approval.id,
                    "approved_by_user_id": approval.decided_by_user_id,
                    "requested_by_user_id": user.id,
                    "mode": self.settings.publish_jobs_mode,
                    "idempotency_key": key,
                },
            )
            schedule_id = schedule.id

        if self.settings.publish_jobs_mode == "celery":
            from app.workers.tasks.publish import execute_publish

            execute_publish.delay(schedule_id)
            return PublishResult(
                "queued", content, schedule, "Nashr navbatga qo‘yildi (Celery worker)."
            )
        return self.execute(schedule_id)

    # ================================================================== worker side
    def execute(self, schedule_id: int) -> PublishResult:
        """Claim a PENDING schedule and publish it. Safe to call concurrently."""
        if self.settings.meta_dry_run:
            return PublishResult("skipped", None, None, "META_DRY_RUN=true")
        if not self._claim(schedule_id):
            schedule = self.schedules.get(schedule_id)
            return PublishResult(
                "skipped", None, schedule, "Schedule is not pending (already claimed or done)."
            )
        return self._run(schedule_id)

    def process_due(self, limit: int = 20) -> dict[str, int]:
        if self.settings.meta_dry_run:
            due = len(self.schedules.list_due(utcnow(), limit=limit))
            if due:
                logger.info("META_DRY_RUN=true: %d due schedule(s) left untouched", due)
            return {"due": due, "processed": 0, "dry_run": 1}
        due_ids = [s.id for s in self.schedules.list_due(utcnow(), limit=limit)]
        counts = {"due": len(due_ids), "processed": 0}
        for sid in due_ids:
            result = self.execute(sid)
            if result.status != "skipped":
                counts["processed"] += 1
                counts[result.status] = counts.get(result.status, 0) + 1
        return counts

    def reconcile_stale(self, limit: int = 20) -> dict[str, int]:
        """Finish or settle schedules stuck in PROCESSING (crash, lost response)."""
        if self.settings.meta_dry_run:
            return {"stale": 0}
        threshold = utcnow() - timedelta(minutes=self.settings.publish_reconcile_after_minutes)
        stale = self.session.scalars(
            select(ContentSchedule)
            .where(
                ContentSchedule.status == ScheduleStatus.PROCESSING,
                ContentSchedule.processing_started_at < threshold,
            )
            .order_by(ContentSchedule.id)
            .limit(limit)
        ).all()
        counts = {"stale": len(stale)}
        for schedule in stale:
            started = schedule.processing_started_at
            claimed = self.session.execute(
                update(ContentSchedule)
                .where(
                    ContentSchedule.id == schedule.id,
                    ContentSchedule.status == ScheduleStatus.PROCESSING,
                    ContentSchedule.processing_started_at == started,
                )
                .values(processing_started_at=utcnow())
            ).rowcount
            self.session.commit()
            if claimed != 1:
                continue
            try:
                result = self._resume(schedule.id)
            except Exception:  # one broken row must not stop the others
                self.session.rollback()
                logger.exception("reconcile failed for schedule %s", schedule.id)
                counts["error"] = counts.get("error", 0) + 1
                continue
            counts[result.status] = counts.get(result.status, 0) + 1
        return counts

    def publishing_limit(self, account: InstagramAccount) -> PublishingLimit:
        token = self._token(account)
        return self._call(token, account.ig_user_id, lambda c: c.publishing_limit())

    # ================================================================== internals
    def _claim(self, schedule_id: int) -> bool:
        claimed = self.session.execute(
            update(ContentSchedule)
            .where(
                ContentSchedule.id == schedule_id,
                ContentSchedule.status == ScheduleStatus.PENDING,
            )
            .values(
                status=ScheduleStatus.PROCESSING,
                processing_started_at=utcnow(),
                attempts=ContentSchedule.attempts + 1,
                outcome_unknown=False,
            )
        ).rowcount
        self.session.commit()
        return claimed == 1

    def _run(self, schedule_id: int) -> PublishResult:
        schedule = self._schedule(schedule_id)
        content = self.contents.get(schedule.content_id)
        if content is None or content.version != schedule.content_version:
            return self._settle_schedule(
                schedule, content, "Kontent rejalashtirilgandan keyin o‘zgargan yoki o‘chirilgan."
            )
        if content.status not in (ContentStatus.SCHEDULED, ContentStatus.FAILED):
            return self._settle_schedule(schedule, content, "Nashr bekor qilingan.")

        readiness = self.review.readiness(content.id)
        blockers = [c.message for c in readiness.checks if c.severity == "blocker" and not c.ok]
        if blockers:
            return self._fail_before_start(schedule, content, "; ".join(blockers))

        account = self.review.publish_account(content)
        if account is None:  # covered by readiness; defensive
            return self._fail_before_start(schedule, content, "Instagram akkaunt topilmadi.")
        version = self.versions.get_version(content.id, content.version)
        plan = build_plan(version)  # type: ignore[arg-type]

        try:
            token = self._token(account)
            limit = self._call(token, account.ig_user_id, lambda c: c.publishing_limit())
        except MetaApiError as exc:
            if exc.kind in RETRYABLE:
                return self._defer(schedule, content, exc.message, minutes=5)
            return self._fail_before_start(schedule, content, _describe(exc))
        if limit.remaining <= 0:
            return self._defer(
                schedule,
                content,
                f"Meta nashr limiti tugagan ({limit.quota_usage}/{limit.quota_total} "
                "24 soatda). Keyinroq avtomatik qayta urinadi.",
                minutes=60,
            )

        try:
            self.content_service.start_publishing(content.id, PUBLISH_ACTOR, from_schedule=True)
        except AppError as exc:
            return self._settle_schedule(schedule, content, exc.message)
        with atomic(self.session):
            schedule.instagram_account_id = account.id
        return self._publish_steps(schedule, content, plan, account, token)

    def _resume(self, schedule_id: int) -> PublishResult:
        schedule = self._schedule(schedule_id)
        content = self.contents.get(schedule.content_id)
        if content is None or content.status != ContentStatus.PUBLISHING:
            # Crashed before start_publishing (nothing sent): let the scheduler retry,
            # but not forever.
            if schedule.attempts >= self.settings.publish_max_attempts:
                return self._settle_schedule(
                    schedule, content, "Nashr bir necha marta boshlanmadi (worker to‘xtagan?)."
                )
            with atomic(self.session):
                schedule.status = ScheduleStatus.PENDING
                schedule.scheduled_at = utcnow()
            return PublishResult("deferred", content, schedule, "requeued")
        account = self.session.get(InstagramAccount, schedule.instagram_account_id or 0)
        version = self.versions.get_version(content.id, schedule.content_version)
        if account is None or version is None:
            return self._fail(schedule, content, "Instagram akkaunt yoki versiya topilmadi.")
        try:
            token = self._token(account)
        except MetaApiError as exc:
            unknown = (
                " Oldingi urinish natijasi noma’lum: post chiqqan-chiqmaganini Instagram’da "
                "tekshiring."
                if schedule.outcome_unknown
                else ""
            )
            return self._fail(schedule, content, _describe(exc) + unknown)
        return self._publish_steps(schedule, content, build_plan(version), account, token)

    def _publish_steps(
        self,
        schedule: ContentSchedule,
        content: Content,
        plan: PublishPlan,
        account: InstagramAccount,
        token: str,
    ) -> PublishResult:
        ig = account.ig_user_id
        try:
            container_id = schedule.ig_container_id
            if container_id:
                status = self._call(token, ig, lambda c: c.container_status(container_id))
                if status == ContainerStatus.PUBLISHED:
                    return self._succeed(schedule, content, plan, token, ig, None, reconciled=True)
                if status in (ContainerStatus.EXPIRED, ContainerStatus.ERROR):
                    if schedule.outcome_unknown:
                        return self._fail(
                            schedule,
                            content,
                            f"Container {status.value}: post nashr qilinmagan. "
                            "Qayta urinish mumkin.",
                            clear_container=True,
                        )
                    container_id = None
                elif status == ContainerStatus.UNKNOWN:
                    container_id = None
            if not container_id:
                container_id = self._create_containers(schedule, content, plan, token, ig)
                self._heartbeat(schedule)

            status = self._wait_finished(token, ig, container_id)
            self._heartbeat(schedule)
            if status == ContainerStatus.PUBLISHED:
                return self._succeed(schedule, content, plan, token, ig, None, reconciled=True)
            if status != ContainerStatus.FINISHED:
                raise MetaApiError(
                    MetaErrorKind.MEDIA_VALIDATION
                    if status == ContainerStatus.ERROR
                    else MetaErrorKind.PUBLISHING_FAILED,
                    meta_message=f"container status {status.value}",
                )
            try:
                media_id = self._call(token, ig, lambda c: c.publish(container_id))
            except PublishOutcomeUnknownError as exc:
                return self._outcome_unknown(schedule, content, plan, token, ig, exc)
            return self._succeed(schedule, content, plan, token, ig, media_id)
        except MetaApiError as exc:
            return self._fail(
                schedule,
                content,
                _describe(exc),
                retry_in=self._retry_minutes(schedule, exc),
                clear_container=exc.kind == MetaErrorKind.MEDIA_VALIDATION,
            )

    def _create_containers(
        self, schedule: ContentSchedule, content: Content, plan: PublishPlan, token: str, ig: str
    ) -> str:
        ids = [self._call(token, ig, lambda c, p=p: c.create_container(p)) for p in plan.items]
        if plan.final is not None:
            params = {**plan.final, "children": ",".join(ids)}
            container_id = self._call(token, ig, lambda c: c.create_container(params))
        else:
            container_id = ids[0]
        with atomic(self.session):
            schedule.ig_container_id = container_id
            schedule.ig_container_created_at = utcnow()
            self.audit.record(
                AuditAction.INSTAGRAM_CONTAINER_CREATED,
                PUBLISH_ACTOR,
                content_id=content.id,
                content_version=schedule.content_version,
                details={
                    "schedule_id": schedule.id,
                    "container_id": container_id,
                    "children": ids if plan.final is not None else [],
                },
            )
        return container_id

    def _heartbeat(self, schedule: ContentSchedule) -> None:
        """Still working on it: keeps reconcile_stale from treating this run as crashed."""
        with atomic(self.session):
            schedule.processing_started_at = utcnow()

    def _wait_finished(self, token: str, ig: str, container_id: str) -> ContainerStatus:
        deadline = time.monotonic() + self.settings.meta_container_max_wait_seconds
        while True:
            status = self._call(token, ig, lambda c: c.container_status(container_id))
            if status != ContainerStatus.IN_PROGRESS:
                return status
            if time.monotonic() >= deadline:
                raise MetaApiError(
                    MetaErrorKind.TRANSIENT,
                    meta_message="container still IN_PROGRESS (video processing); will retry",
                )
            self._sleep(self.settings.meta_container_poll_interval_seconds)

    def _outcome_unknown(
        self,
        schedule: ContentSchedule,
        content: Content,
        plan: PublishPlan,
        token: str,
        ig: str,
        exc: PublishOutcomeUnknownError,
    ) -> PublishResult:
        with atomic(self.session):
            schedule.outcome_unknown = True
            schedule.last_error = (
                "Meta javobi kelmadi — natija container holati bo‘yicha tekshiriladi"
            )
            self.audit.record(
                AuditAction.CONTENT_PUBLISH_FAILED,
                PUBLISH_ACTOR,
                content_id=content.id,
                content_version=schedule.content_version,
                status="UNKNOWN",
                error=str(exc.details),
                details={"schedule_id": schedule.id, "container_id": schedule.ig_container_id},
            )
        try:  # one immediate check; otherwise the reconcile task decides later
            status = self._call(
                token, ig, lambda c: c.container_status(schedule.ig_container_id or "")
            )
        except MetaApiError:
            status = ContainerStatus.UNKNOWN
        if status == ContainerStatus.PUBLISHED:
            return self._succeed(schedule, content, plan, token, ig, None, reconciled=True)
        return PublishResult(
            "in_progress",
            content,
            schedule,
            "Meta javobi kelmadi. Post holati avtomatik tekshiriladi; qayta bosmang.",
        )

    def _succeed(
        self,
        schedule: ContentSchedule,
        content: Content,
        plan: PublishPlan,
        token: str,
        ig: str,
        media_id: str | None,
        *,
        reconciled: bool = False,
    ) -> PublishResult:
        permalink = None
        if media_id is None:  # published, but the media id never reached us
            media_id, permalink = self._find_media(token, ig, plan, schedule)
        if media_id and not permalink:
            try:
                permalink = self._call(token, ig, lambda c: c.media_info(media_id)).permalink
            except MetaApiError:
                permalink = None
        approval = self.approvals.approvals.get(schedule.approval_id)
        details = {
            "schedule_id": schedule.id,
            "container_id": schedule.ig_container_id,
            "approval_id": schedule.approval_id,
            "approved_by_user_id": approval.decided_by_user_id if approval else None,
            "requested_by_user_id": schedule.created_by_user_id,
            "instagram_account_id": schedule.instagram_account_id,
            "reconciled": reconciled,
        }
        with atomic(self.session):
            schedule.ig_media_id = media_id
            schedule.outcome_unknown = False
            schedule.last_error = None
            content = self.content_service.mark_published(
                content.id,
                PUBLISH_ACTOR,
                ig_media_id=media_id,
                permalink=permalink,
                details=details,
            )
            if reconciled:
                self.audit.record(
                    AuditAction.CONTENT_PUBLISH_RECONCILED,
                    PUBLISH_ACTOR,
                    content_id=content.id,
                    content_version=schedule.content_version,
                    details={**details, "ig_media_id": media_id},
                )
        return PublishResult("published", content, schedule, "Instagram’da nashr qilindi.")

    def _find_media(
        self, token: str, ig: str, plan: PublishPlan, schedule: ContentSchedule
    ) -> tuple[str | None, str | None]:
        try:
            recent = self._call(token, ig, lambda c: c.recent_media(limit=10))
        except MetaApiError:
            return None, None
        for item in recent:
            if plan.caption and (item.caption or "").strip() == plan.caption.strip():
                return item.media_id, item.permalink
        return None, None

    def _fail(
        self,
        schedule: ContentSchedule,
        content: Content,
        message: str,
        *,
        retry_in: int | None = None,
        clear_container: bool = False,
    ) -> PublishResult:
        content = self.content_service.mark_publish_failed(content.id, PUBLISH_ACTOR, error=message)
        with atomic(self.session):
            schedule.outcome_unknown = False
            schedule.last_error = message[:2000]
            if clear_container:
                schedule.ig_container_id = None
                schedule.ig_container_created_at = None
            if retry_in is not None:
                schedule.status = ScheduleStatus.PENDING
                schedule.scheduled_at = utcnow() + timedelta(minutes=retry_in)
            else:
                schedule.status = ScheduleStatus.FAILED
        tail = f" Avtomatik qayta urinish {retry_in} daqiqadan keyin." if retry_in else ""
        return PublishResult("failed", content, schedule, message + tail)

    def _fail_before_start(
        self, schedule: ContentSchedule, content: Content, message: str
    ) -> PublishResult:
        """Preflight failed: nothing was sent to Meta."""
        if self.approvals.get_valid_approval(content) is not None and content.status in (
            ContentStatus.APPROVED,
            ContentStatus.SCHEDULED,
            ContentStatus.FAILED,
        ):
            try:
                self.content_service.start_publishing(content.id, PUBLISH_ACTOR)
                return self._fail(schedule, content, message)
            except AppError:
                pass
        return self._settle_schedule(schedule, content, message)

    def _settle_schedule(
        self, schedule: ContentSchedule, content: Content | None, message: str
    ) -> PublishResult:
        with atomic(self.session):
            schedule.status = ScheduleStatus.FAILED
            schedule.last_error = message[:2000]
            if content is not None:
                self._release(content, message)
            self.audit.record(
                AuditAction.CONTENT_PUBLISH_FAILED,
                PUBLISH_ACTOR,
                content_id=content.id if content else None,
                content_version=schedule.content_version,
                status="FAILED",
                error=message,
                details={"schedule_id": schedule.id, "stage": "preflight"},
            )
        return PublishResult("failed", content, schedule, message)

    def _release(self, content: Content, reason: str) -> None:
        """A schedule ended before Meta was contacted. Don't leave the content showing
        SCHEDULED: back to APPROVED, or to review when its approval no longer holds."""
        if content.status not in (ContentStatus.SCHEDULED, ContentStatus.APPROVED):
            return
        if self.approvals.get_valid_approval(content) is None:
            invalidate_active_approvals(self.session, self.audit, content, PUBLISH_ACTOR, reason)
            apply_transition(content, ContentStatus.READY_FOR_REVIEW)
        elif (
            content.status == ContentStatus.SCHEDULED
            and not self.schedules.list_pending_for_content(content.id)
        ):
            apply_transition(content, ContentStatus.APPROVED)

    def _defer(
        self, schedule: ContentSchedule, content: Content, message: str, *, minutes: int
    ) -> PublishResult:
        with atomic(self.session):
            schedule.status = ScheduleStatus.PENDING
            # Waiting for quota is not a failed attempt.
            schedule.attempts = max(schedule.attempts - 1, 0)
            schedule.scheduled_at = utcnow() + timedelta(minutes=minutes)
            schedule.last_error = message
            self.audit.record(
                AuditAction.CONTENT_PUBLISH_DEFERRED,
                PUBLISH_ACTOR,
                content_id=content.id,
                content_version=schedule.content_version,
                details={
                    "schedule_id": schedule.id,
                    "retry_in_minutes": minutes,
                    "reason": message,
                },
            )
        return PublishResult("deferred", content, schedule, message)

    def _retry_minutes(self, schedule: ContentSchedule, exc: MetaApiError) -> int | None:
        if exc.kind not in RETRYABLE or schedule.attempts >= self.settings.publish_max_attempts:
            return None
        return 60 if exc.kind == MetaErrorKind.RATE_LIMIT else 5 * max(schedule.attempts, 1)

    def _token(self, account: InstagramAccount) -> str:
        try:
            token = InstagramAccountService(self.session, self.audit).get_access_token(
                account.id, PUBLISH_ACTOR
            )
        except DecryptionError as exc:  # key rotated away / corrupted ciphertext
            raise MetaApiError(
                MetaErrorKind.TOKEN_EXPIRED, meta_message="stored token cannot be decrypted"
            ) from exc
        if not token:
            raise MetaApiError(MetaErrorKind.TOKEN_EXPIRED)
        return token

    def _call(
        self, token: str, ig_user_id: str, fn: Callable[[InstagramPublishingClient], Any]
    ) -> Any:
        """Run one client call on a fresh client (each run_sync uses its own event loop)."""

        async def go() -> Any:
            client = self.client_factory(token, ig_user_id)
            try:
                return await fn(client)
            finally:
                await client.aclose()

        return run_sync(go())

    def _content(self, content_id: int) -> Content:
        content = self.contents.get(content_id)
        if content is None:
            raise NotFoundError("Content not found")
        return content

    def _schedule(self, schedule_id: int) -> ContentSchedule:
        schedule = self.schedules.get(schedule_id)
        if schedule is None:
            raise NotFoundError("Schedule not found")
        self.session.refresh(schedule)
        return schedule


def _describe(exc: MetaApiError) -> str:
    meta = (exc.details or {}).get("meta_message") if isinstance(exc.details, dict) else None
    return f"{exc.message} (Meta: {meta})" if meta else exc.message
