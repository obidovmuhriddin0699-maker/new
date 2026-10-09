"""Publishing and media endpoints.

Publishing is a human (OWNER/ADMIN) request; the backend publish service re-verifies the
approval and the preflight before anything reaches Meta. There is no endpoint an AI
agent could use to publish.
"""

from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Query, Request, status
from fastapi.responses import FileResponse
from starlette.concurrency import run_in_threadpool

from app.api.deps import DbSession, HumanActorDep, limit_per_user
from app.api.v1.contents import _read
from app.core.config import get_settings
from app.core.ratelimit import PUBLISH, UPLOAD
from app.schemas.content import ContentRead, PublishStateRead
from app.schemas.errors import error_responses
from app.schemas.publish import (
    AssetUrlRequest,
    PublishPlanRead,
    PublishPreviewRead,
    PublishRequest,
    PublishResponse,
    PublishStepRead,
)
from app.schemas.review import ReadinessCheckRead, ReadinessRead
from app.services.content import AssetInput, ContentService
from app.services.media_storage import MediaRejectedError, MediaStorage
from app.services.publish import PublishPreview, PublishService

router = APIRouter(prefix="/contents", tags=["publishing"])
media_router = APIRouter(prefix="/media", tags=["media"])

_URL_MIME = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".mp4": "video/mp4",
    ".mov": "video/quicktime",
}


def _preview(p: PublishPreview) -> PublishPreviewRead:
    r = p.readiness
    plan = None
    if p.plan is not None:
        plan = PublishPlanRead(
            content_type=p.plan.content_type.value,
            version=p.plan.version,
            caption=p.plan.caption,
            caption_length=len(p.plan.caption),
            account_username=p.plan.account_username,
            steps=[
                PublishStepRead(endpoint=s.endpoint, params=s.params, note=s.note)
                for s in p.plan.steps()
            ],
        )
    return PublishPreviewRead(
        dry_run=p.dry_run,
        ready=r.ready,
        problems=p.problems,
        readiness=ReadinessRead(
            ready=r.ready,
            content_id=r.content_id,
            version=r.version,
            checks=[
                ReadinessCheckRead(key=c.key, ok=c.ok, severity=c.severity, message=c.message)
                for c in r.checks
            ],
        ),
        plan=plan,
    )


@router.get(
    "/{content_id}/publish-preview",
    response_model=PublishPreviewRead,
    summary="What would be sent to Instagram (no Meta call)",
    description="Preflight checks plus the exact container parameters built from the approved "
    "version snapshot. Tokens are never included.",
    responses=error_responses(401, 404),
)
def publish_preview(content_id: int, db: DbSession, _: HumanActorDep) -> PublishPreviewRead:
    return _preview(PublishService(db).preview(content_id))


@router.post(
    "/{content_id}/publish",
    response_model=PublishResponse,
    summary="Publish the approved version now (human OWNER/ADMIN only)",
    description=(
        "Re-verifies the human approval of `expected_version` (hash, approver, expiry) and the "
        "preflight, then creates the Instagram container and publishes it. Idempotent per "
        "version: a version is never published twice. With `META_DRY_RUN=true` nothing is "
        "sent to Meta and the response is the preview (`status=dry_run`)."
    ),
    responses=error_responses(401, 403, 404, 409, 422),
    dependencies=[limit_per_user(PUBLISH)],
)
def publish(
    content_id: int, body: PublishRequest, db: DbSession, actor: HumanActorDep
) -> PublishResponse:
    result = PublishService(db).request_publish(
        content_id, actor, expected_version=body.expected_version
    )
    service = ContentService(db)
    content = service.get(content_id)
    return PublishResponse(
        status=result.status,
        message=result.message,
        content=_read(service, content),
        publish_state=PublishStateRead.model_validate(result.schedule) if result.schedule else None,
        preview=_preview(result.preview) if result.preview else None,
    )


# ------------------------------------------------------------------ media
@router.post(
    "/{content_id}/assets",
    response_model=ContentRead,
    status_code=status.HTTP_201_CREATED,
    summary="Attach media by public HTTPS URL",
    description="The URL must be publicly reachable over HTTPS (Meta downloads it at publish "
    "time). Adding media creates a new content version, so it must be approved again.",
    responses=error_responses(401, 403, 404, 409, 422),
    dependencies=[limit_per_user(UPLOAD)],
)
def attach_asset_url(
    content_id: int, body: AssetUrlRequest, db: DbSession, actor: HumanActorDep
) -> ContentRead:
    service = ContentService(db)
    suffix = Path(body.public_url.split("?", 1)[0]).suffix.lower()
    service.add_asset(
        content_id,
        actor,
        expected_version=body.expected_version,
        asset=AssetInput(
            kind=body.kind,
            position=body.position
            if body.position is not None
            else _next_position(service, content_id),
            public_url=body.public_url,
            mime_type=body.mime_type or _URL_MIME.get(suffix),
            provider="url",
        ),
    )
    return _read(service, service.get(content_id))


@router.post(
    "/{content_id}/assets/upload",
    response_model=ContentRead,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a JPEG image or MP4/MOV video (raw request body)",
    description="Validated by content (magic bytes), size-limited, stored with a random name "
    "and served at `{MEDIA_PUBLIC_BASE_URL}/media/<name>` for Meta to download. Creates a new "
    "content version (re-approval needed).",
    responses=error_responses(401, 403, 404, 409, 422),
    dependencies=[limit_per_user(UPLOAD)],
)
async def upload_asset(
    content_id: int,
    request: Request,
    db: DbSession,
    actor: HumanActorDep,
    expected_version: Annotated[int, Query(ge=1)],
    position: Annotated[int | None, Query(ge=0, le=20)] = None,
) -> ContentRead:
    s = get_settings()
    limit = max(s.media_max_image_mb, s.media_max_video_mb) * 1024 * 1024
    chunks: list[bytes] = []
    size = 0
    async for chunk in request.stream():
        size += len(chunk)
        if size > limit:
            raise MediaRejectedError(f"Fayl juda katta (chegara {limit // (1024 * 1024)} MB).")
        chunks.append(chunk)
    data = b"".join(chunks)

    def store() -> None:
        storage = MediaStorage()
        stored = storage.save(data)
        try:
            service.add_asset(
                content_id,
                actor,
                expected_version=expected_version,
                asset=AssetInput(
                    kind=stored.kind,
                    position=position
                    if position is not None
                    else _next_position(service, content_id),
                    storage_path=stored.name,
                    public_url=stored.public_url,
                    mime_type=stored.mime_type,
                    width=stored.width,
                    height=stored.height,
                    checksum_sha256=stored.sha256,
                    provider="upload",
                ),
            )
        except Exception:
            (storage.root / stored.name).unlink(missing_ok=True)  # no orphan files
            raise

    service = ContentService(db)
    await run_in_threadpool(store)
    return await run_in_threadpool(lambda: _read(service, service.get(content_id)))


@router.delete(
    "/{content_id}/assets/{asset_id}",
    response_model=ContentRead,
    summary="Remove media (creates a new version; re-approval needed)",
    responses=error_responses(401, 403, 404, 409),
)
def remove_asset(
    content_id: int,
    asset_id: int,
    db: DbSession,
    actor: HumanActorDep,
    expected_version: Annotated[int, Query(ge=1)],
) -> ContentRead:
    service = ContentService(db)
    service.remove_asset(content_id, asset_id, actor, expected_version=expected_version)
    return _read(service, service.get(content_id))


@media_router.get(
    "/{name}",
    summary="Public media file (Meta downloads post media from here)",
    description="Unauthenticated by design: Meta's servers fetch it. Names are random "
    "(192-bit) and only uploaded files are served.",
    responses=error_responses(404),
)
def media_file(name: str) -> FileResponse:
    storage = MediaStorage()
    path = storage.path_for(name)
    return FileResponse(
        path,
        media_type=storage.mime_for(name),
        headers={
            "Cache-Control": "public, max-age=86400",
            "X-Content-Type-Options": "nosniff",
            "Content-Disposition": "inline",
        },
    )


def _next_position(service: ContentService, content_id: int) -> int:
    return len(service.list_assets(content_id))
