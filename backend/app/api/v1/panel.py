"""Admin panel endpoints: overview, calendar, audit log, brand profiles, media library."""

from datetime import date
from typing import Annotated

from fastapi import APIRouter, Query, status
from sqlalchemy import func, select

from app.api.deps import DbSession, HumanActorDep
from app.core.errors import PermissionDeniedError
from app.models import AuditLog, Content, ContentAsset
from app.schemas.errors import error_responses
from app.schemas.panel import (
    AssetList,
    AssetListItem,
    AuditEventPanelRead,
    AuditLogList,
    BrandProfileCreate,
    BrandProfileRead,
    BrandProfileUpdate,
    CalendarItemRead,
    CalendarRead,
    DashboardSummaryRead,
    UpcomingItem,
)
from app.services import BrandProfileService
from app.services.dashboard import DashboardService
from app.services.guards import WRITER_ROLES, require_active_human

router = APIRouter(tags=["panel"])


@router.get(
    "/dashboard/summary",
    response_model=DashboardSummaryRead,
    summary="Overview counters",
    responses=error_responses(401),
)
def dashboard_summary(db: DbSession, _: HumanActorDep) -> DashboardSummaryRead:
    s = DashboardService(db).summary()
    return DashboardSummaryRead(
        total=s.total,
        by_status=s.by_status,
        pending_approval=s.pending_approval,
        scheduled=s.scheduled,
        published=s.published,
        failed=s.failed,
        drafts=s.drafts,
        reach=s.reach,
        engagement_rate=s.engagement_rate,
        analytics_available=s.analytics_available,
        upcoming=[UpcomingItem(**u) for u in s.upcoming],
    )


@router.get(
    "/calendar",
    response_model=CalendarRead,
    summary="Calendar items in a date range",
    description="Scheduled, published and planned content (max 62 days).",
    responses=error_responses(400, 401, 422),
)
def calendar(db: DbSession, _: HumanActorDep, start: date, end: date) -> CalendarRead:
    items = DashboardService(db).calendar(start, end)
    return CalendarRead(
        start=start,
        end=end,
        items=[
            CalendarItemRead(**{f: getattr(i, f) for f in CalendarItemRead.model_fields})
            for i in items
        ],
    )


@router.get(
    "/audit-logs",
    response_model=AuditLogList,
    summary="System / audit log",
    description="OWNER and ADMIN only. Append-only; secrets are redacted at write time.",
    responses=error_responses(401, 403),
)
def audit_logs(
    db: DbSession,
    actor: HumanActorDep,
    action: Annotated[str | None, Query(max_length=100)] = None,
    content_id: int | None = None,
    status_: Annotated[str | None, Query(alias="status", max_length=30)] = None,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
) -> AuditLogList:
    user = require_active_human(db, actor)
    if user.role not in WRITER_ROLES:
        raise PermissionDeniedError("Only owners and admins can read the system log")
    stmt = select(AuditLog)
    if action:
        stmt = stmt.where(AuditLog.action == action)
    if content_id is not None:
        stmt = stmt.where(AuditLog.content_id == content_id)
    if status_:
        stmt = stmt.where(AuditLog.status == status_)
    total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    rows = db.scalars(stmt.order_by(AuditLog.id.desc()).offset(offset).limit(limit)).all()
    return AuditLogList(
        items=[AuditEventPanelRead.model_validate(r) for r in rows],
        total=total,
        offset=offset,
        limit=limit,
    )


@router.get(
    "/brand-profiles",
    response_model=list[BrandProfileRead],
    summary="Brand profiles",
    responses=error_responses(401),
)
def list_brands(db: DbSession, _: HumanActorDep) -> list[BrandProfileRead]:
    return [BrandProfileRead.model_validate(b) for b in BrandProfileService(db).list()]


@router.get(
    "/brand-profiles/{profile_id}",
    response_model=BrandProfileRead,
    summary="Brand profile",
    responses=error_responses(401, 404),
)
def get_brand(profile_id: int, db: DbSession, _: HumanActorDep) -> BrandProfileRead:
    return BrandProfileRead.model_validate(BrandProfileService(db).get(profile_id))


@router.post(
    "/brand-profiles",
    response_model=BrandProfileRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create brand profile",
    responses=error_responses(401, 403, 409, 422),
)
def create_brand(body: BrandProfileCreate, db: DbSession, actor: HumanActorDep) -> BrandProfileRead:
    data = body.model_dump(exclude_none=True)
    make_default = data.pop("make_default", False)
    return BrandProfileRead.model_validate(
        BrandProfileService(db).create(actor, make_default=make_default, **data)
    )


@router.patch(
    "/brand-profiles/{profile_id}",
    response_model=BrandProfileRead,
    summary="Update brand profile",
    responses=error_responses(401, 403, 404, 422),
)
def update_brand(
    profile_id: int, body: BrandProfileUpdate, db: DbSession, actor: HumanActorDep
) -> BrandProfileRead:
    changes = body.model_dump(exclude_unset=True)
    return BrandProfileRead.model_validate(
        BrandProfileService(db).update(profile_id, actor, **changes)
    )


@router.get(
    "/assets",
    response_model=AssetList,
    summary="Media library",
    description="Asset metadata of non-deleted content. No files are generated "
    "while no media provider is configured.",
    responses=error_responses(401),
)
def list_assets(
    db: DbSession,
    _: HumanActorDep,
    content_id: int | None = None,
    limit: Annotated[int, Query(ge=1, le=200)] = 100,
) -> AssetList:
    stmt = (
        select(ContentAsset)
        .join(Content, Content.id == ContentAsset.content_id)
        .where(ContentAsset.deleted_at.is_(None), Content.deleted_at.is_(None))
    )
    if content_id is not None:
        stmt = stmt.where(ContentAsset.content_id == content_id)
    total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    rows = db.scalars(stmt.order_by(ContentAsset.id.desc()).limit(limit)).all()
    return AssetList(items=[AssetListItem.model_validate(r) for r in rows], total=total)
