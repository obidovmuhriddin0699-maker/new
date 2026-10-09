from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict

from app.models.enums import ApprovalChannel, ApprovalDecision


class ReadinessCheckRead(BaseModel):
    key: str
    ok: bool
    severity: Literal["blocker", "warning", "info"]
    message: str


class ReadinessRead(BaseModel):
    ready: bool
    content_id: int
    version: int
    checks: list[ReadinessCheckRead]
    note: str = "Read-only preflight. Publishing itself arrives in PHASE 8."


class FieldDiffRead(BaseModel):
    field: str
    changed: bool
    old: Any = None
    new: Any = None
    lines: list[dict[str, str]] = []


class VersionDiffRead(BaseModel):
    content_id: int
    from_version: int
    to_version: int
    from_label: str
    changed_fields: list[str]
    fields: list[FieldDiffRead]


class ApprovalLogItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    content_id: int
    content_topic: str | None = None
    content_version: int
    decision: ApprovalDecision
    decided_by_user_id: int
    decided_by_email: str | None = None
    channel: ApprovalChannel
    comment: str | None
    created_at: datetime
    invalidated_at: datetime | None
    invalidation_reason: str | None
    active: bool = False


class ApprovalLog(BaseModel):
    items: list[ApprovalLogItem]
    total: int
    offset: int
    limit: int
