"""Approval decisions log (who decided what, on which version, via which channel)."""

from typing import Annotated

from fastapi import APIRouter, Query
from sqlalchemy import func, select

from app.api.deps import DbSession, HumanActorDep
from app.models import Approval, Content, User
from app.models.enums import ApprovalChannel, ApprovalDecision
from app.schemas.errors import error_responses
from app.schemas.review import ApprovalLog, ApprovalLogItem

router = APIRouter(prefix="/approvals", tags=["approvals"])


@router.get(
    "",
    response_model=ApprovalLog,
    summary="Approval decisions log",
    responses=error_responses(401, 422),
)
def approvals_log(
    db: DbSession,
    _: HumanActorDep,
    decision: ApprovalDecision | None = None,
    channel: ApprovalChannel | None = None,
    active_only: bool = False,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
) -> ApprovalLog:
    stmt = (
        select(Approval, Content.topic, User.email)
        .join(Content, Content.id == Approval.content_id)
        .join(User, User.id == Approval.decided_by_user_id)
    )
    if decision is not None:
        stmt = stmt.where(Approval.decision == decision)
    if channel is not None:
        stmt = stmt.where(Approval.channel == channel)
    if active_only:
        stmt = stmt.where(
            Approval.decision == ApprovalDecision.APPROVED, Approval.invalidated_at.is_(None)
        )
    total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    rows = db.execute(stmt.order_by(Approval.id.desc()).offset(offset).limit(limit)).all()
    items = []
    for approval, topic, email in rows:
        item = ApprovalLogItem.model_validate(approval)
        item.content_topic = topic
        item.decided_by_email = email
        item.active = approval.is_active_approval
        items.append(item)
    return ApprovalLog(items=items, total=total, offset=offset, limit=limit)
