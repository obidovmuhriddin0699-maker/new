"""Content endpoints. Routers only translate HTTP <-> service calls.

Publishing and media endpoints live in ``publishing.py``.
"""

from typing import Annotated, Literal

from fastapi import APIRouter, Query, status

from app.api.deps import DbSession, HumanActorDep
from app.models import Content
from app.models.enums import ContentStatus, ContentType, ScheduleStatus
from app.schemas.content import (
    ApprovalRead,
    ApprovalResponse,
    AssetRead,
    AuditEventRead,
    ContentCreate,
    ContentHistoryRead,
    ContentList,
    ContentRead,
    ContentUpdate,
    ContentVersionRead,
    DecisionRequest,
    PublishStateRead,
)
from app.schemas.errors import error_responses
from app.schemas.panel import ScheduleRead, ScheduleRequest
from app.schemas.review import FieldDiffRead, ReadinessCheckRead, ReadinessRead, VersionDiffRead
from app.services import ApprovalService, ContentService, ScheduleService
from app.services.review import ReviewService

router = APIRouter(prefix="/contents", tags=["contents"])


def _read(service: ContentService, content: Content) -> ContentRead:
    data = ContentRead.model_validate(content)
    data.assets = [AssetRead.model_validate(a) for a in service.list_assets(content.id)]
    data.publish_authorized = service.is_publish_authorized(content)
    pending = [
        sch
        for sch in service.schedules.list_pending_for_content(content.id)
        if sch.content_version == content.version
    ]
    data.scheduled_at = pending[0].scheduled_at if pending else None
    attempts = [
        sch
        for sch in service.schedules.list_for_content(content.id)
        if sch.content_version == content.version and sch.status != ScheduleStatus.CANCELLED
    ]
    data.publish_state = PublishStateRead.model_validate(attempts[-1]) if attempts else None
    return data


@router.get(
    "",
    response_model=ContentList,
    summary="List content",
    description="Paginated list of non-deleted content, newest first.",
    responses=error_responses(401, 422),
)
def list_contents(
    db: DbSession,
    _: HumanActorDep,
    status_: Annotated[ContentStatus | None, Query(alias="status")] = None,
    content_type: ContentType | None = None,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    sort: Literal["newest", "oldest", "updated", "waiting"] = "newest",
) -> ContentList:
    service = ContentService(db)
    rows, total = service.list(
        status=status_, content_type=content_type, offset=offset, limit=limit, sort=sort
    )
    return ContentList(
        items=[_read(service, c) for c in rows], total=total, offset=offset, limit=limit
    )


@router.post(
    "",
    response_model=ContentRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create content (DRAFT, version 1)",
    responses=error_responses(401, 403, 422),
)
def create_content(body: ContentCreate, db: DbSession, actor: HumanActorDep) -> ContentRead:
    service = ContentService(db)
    data = body.model_dump(exclude_none=True)
    content = service.create(
        actor,
        content_type=data.pop("content_type"),
        language=data.pop("language"),
        **data,
    )
    return _read(service, content)


@router.get(
    "/{content_id}",
    response_model=ContentRead,
    summary="Get content",
    responses=error_responses(401, 404),
)
def get_content(content_id: int, db: DbSession, _: HumanActorDep) -> ContentRead:
    service = ContentService(db)
    return _read(service, service.get(content_id))


@router.patch(
    "/{content_id}",
    response_model=ContentRead,
    summary="Edit content (creates a new version)",
    description=(
        "Any change to publishable fields creates a new immutable version. "
        "Approvals of earlier versions stop authorising publishing, pending "
        "schedules are cancelled, and APPROVED/SCHEDULED content returns to "
        "READY_FOR_REVIEW. `expected_version` must match the current version."
    ),
    responses=error_responses(401, 403, 404, 409, 422),
)
def update_content(
    content_id: int, body: ContentUpdate, db: DbSession, actor: HumanActorDep
) -> ContentRead:
    service = ContentService(db)
    content = service.update(
        content_id,
        actor,
        expected_version=body.expected_version,
        changes=body.changes(),
        change_note=body.change_note,
    )
    return _read(service, content)


@router.post(
    "/{content_id}/submit-review",
    response_model=ContentRead,
    summary="Submit for human review",
    description="DRAFT or EDIT_REQUESTED → READY_FOR_REVIEW.",
    responses=error_responses(401, 403, 404, 409),
)
def submit_review(content_id: int, db: DbSession, actor: HumanActorDep) -> ContentRead:
    service = ContentService(db)
    return _read(service, service.submit_for_review(content_id, actor))


@router.post(
    "/{content_id}/request-edit",
    response_model=ContentRead,
    summary="Request changes (human only)",
    description=(
        "READY_FOR_REVIEW / APPROVED / SCHEDULED → EDIT_REQUESTED. Invalidates any "
        "active approval and cancels pending schedules."
    ),
    responses=error_responses(401, 403, 404, 409, 422),
)
def request_edit(
    content_id: int, body: DecisionRequest, db: DbSession, actor: HumanActorDep
) -> ContentRead:
    ApprovalService(db).request_edit(
        content_id, actor, expected_version=body.expected_version, comment=body.comment
    )
    service = ContentService(db)
    return _read(service, service.get(content_id))


@router.post(
    "/{content_id}/approve",
    response_model=ApprovalResponse,
    summary="Approve the reviewed version (human only)",
    description=(
        "Records a human approval bound to the exact version and content hash. "
        "Requires an authenticated human session with OWNER/ADMIN role; AI agents "
        "cannot call this. Idempotent: repeating it for the same version returns "
        "the existing approval. **Does not publish.**"
    ),
    responses=error_responses(401, 403, 404, 409, 422),
)
def approve(
    content_id: int, body: DecisionRequest, db: DbSession, actor: HumanActorDep
) -> ApprovalResponse:
    result = ApprovalService(db).approve(
        content_id, actor, expected_version=body.expected_version, comment=body.comment
    )
    service = ContentService(db)
    return ApprovalResponse(
        content=_read(service, result.content),
        approval=ApprovalRead.model_validate(result.approval),
        created=result.created,
    )


@router.post(
    "/{content_id}/reject",
    response_model=ContentRead,
    summary="Reject (human only, terminal)",
    description="READY_FOR_REVIEW → REJECTED. Rejected content can never be published.",
    responses=error_responses(401, 403, 404, 409, 422),
)
def reject(
    content_id: int, body: DecisionRequest, db: DbSession, actor: HumanActorDep
) -> ContentRead:
    ApprovalService(db).reject(
        content_id, actor, expected_version=body.expected_version, comment=body.comment
    )
    service = ContentService(db)
    return _read(service, service.get(content_id))


@router.get(
    "/{content_id}/history",
    response_model=ContentHistoryRead,
    summary="Versions, approval decisions and audit events",
    responses=error_responses(401, 404),
)
def history(content_id: int, db: DbSession, _: HumanActorDep) -> ContentHistoryRead:
    h = ContentService(db).history(content_id)
    return ContentHistoryRead(
        content_id=h.content.id,
        current_version=h.content.version,
        status=h.content.status,
        versions=[ContentVersionRead.model_validate(v) for v in h.versions],
        approvals=[ApprovalRead.model_validate(a) for a in h.approvals],
        events=[AuditEventRead.model_validate(e) for e in h.events],
    )


@router.post(
    "/{content_id}/schedule",
    response_model=ScheduleRead,
    summary="Schedule the approved version (human only)",
    description=(
        "Requires a valid human approval of the current version. Idempotent per version. "
        "The publish worker (Celery beat) publishes it at `scheduled_at`."
    ),
    responses=error_responses(401, 403, 404, 409, 422),
)
def schedule(
    content_id: int, body: ScheduleRequest, db: DbSession, actor: HumanActorDep
) -> ScheduleRead:
    result = ScheduleService(db).schedule(content_id, actor, scheduled_at=body.scheduled_at)
    data = ScheduleRead.model_validate(result.schedule)
    data.created = result.created
    return data


@router.delete(
    "/{content_id}/schedule",
    response_model=ContentRead,
    summary="Cancel the schedule (back to APPROVED)",
    responses=error_responses(401, 403, 404, 409),
)
def unschedule(content_id: int, db: DbSession, actor: HumanActorDep) -> ContentRead:
    ScheduleService(db).unschedule(content_id, actor)
    service = ContentService(db)
    return _read(service, service.get(content_id))


@router.delete(
    "/{content_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete content (soft delete)",
    description="Invalidates approvals and cancels schedules. Not allowed while publishing.",
    responses=error_responses(401, 403, 404, 409),
)
def delete_content(content_id: int, db: DbSession, actor: HumanActorDep) -> None:
    ContentService(db).soft_delete(content_id, actor)


@router.get(
    "/{content_id}/readiness",
    response_model=ReadinessRead,
    summary="Publish readiness checklist (preflight)",
    description="Read-only. Shows every condition that must hold before publishing "
    "(status, valid human approval of this version, quality, format, media, Instagram account, "
    "publisher). The publisher runs exactly these checks before contacting Meta.",
    responses=error_responses(401, 404),
)
def readiness(content_id: int, db: DbSession, _: HumanActorDep) -> ReadinessRead:
    r = ReviewService(db).readiness(content_id)
    return ReadinessRead(
        ready=r.ready,
        content_id=r.content_id,
        version=r.version,
        checks=[
            ReadinessCheckRead(key=c.key, ok=c.ok, severity=c.severity, message=c.message)
            for c in r.checks
        ],
    )


@router.get(
    "/{content_id}/diff",
    response_model=VersionDiffRead,
    summary="What changed between two versions",
    description="Defaults: compare the current version with the last approved one (or the "
    "previous version). Text fields include a line diff.",
    responses=error_responses(400, 401, 404),
)
def diff(
    content_id: int,
    db: DbSession,
    _: HumanActorDep,
    from_version: Annotated[int | None, Query(ge=1)] = None,
    to_version: Annotated[int | None, Query(ge=1)] = None,
) -> VersionDiffRead:
    d = ReviewService(db).diff(content_id, from_version, to_version)
    return VersionDiffRead(
        content_id=d.content_id,
        from_version=d.from_version,
        to_version=d.to_version,
        from_label=d.from_label,
        changed_fields=d.changed_fields,
        fields=[
            FieldDiffRead(field=f.field, changed=f.changed, old=f.old, new=f.new, lines=f.lines)
            for f in d.fields
        ],
    )


@router.post(
    "/{content_id}/revoke-approval",
    response_model=ContentRead,
    summary="Revoke the approval (human only)",
    description="APPROVED / SCHEDULED -> READY_FOR_REVIEW. The approval stops authorising "
    "publishing and pending schedules are cancelled.",
    responses=error_responses(401, 403, 404, 409, 422),
)
def revoke_approval(
    content_id: int, body: DecisionRequest, db: DbSession, actor: HumanActorDep
) -> ContentRead:
    ApprovalService(db).revoke(
        content_id, actor, expected_version=body.expected_version, comment=body.comment
    )
    service = ContentService(db)
    return _read(service, service.get(content_id))
