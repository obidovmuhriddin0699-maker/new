from collections.abc import Sequence
from datetime import datetime
from typing import Any

from sqlalchemy import select

from app.models import AIJob, AnalyticsSnapshot, AuditLog, BrandProfile, SystemSetting
from app.models.enums import AIJobStatus
from app.repositories.base import BaseRepository


class BrandProfileRepository(BaseRepository[BrandProfile]):
    model = BrandProfile

    def get_by_name(self, name: str) -> BrandProfile | None:
        return self.session.scalar(self._select().where(BrandProfile.name == name))

    def get_default(self) -> BrandProfile | None:
        return self.session.scalar(self._select().where(BrandProfile.is_default.is_(True)))


class AIJobRepository(BaseRepository[AIJob]):
    model = AIJob

    def list_by_status(self, status: AIJobStatus, limit: int = 50) -> Sequence[AIJob]:
        return self.session.scalars(
            select(AIJob).where(AIJob.status == status).order_by(AIJob.created_at).limit(limit)
        ).all()


class AuditLogRepository(BaseRepository[AuditLog]):
    """Append-only: exposes add/read only — never update or delete."""

    model = AuditLog

    def list_for_content(self, content_id: int) -> Sequence[AuditLog]:
        return self.session.scalars(
            select(AuditLog).where(AuditLog.content_id == content_id).order_by(AuditLog.id)
        ).all()

    def list_recent(self, limit: int = 100, action: str | None = None) -> Sequence[AuditLog]:
        stmt = select(AuditLog)
        if action:
            stmt = stmt.where(AuditLog.action == action)
        return self.session.scalars(stmt.order_by(AuditLog.id.desc()).limit(limit)).all()


class AnalyticsSnapshotRepository(BaseRepository[AnalyticsSnapshot]):
    model = AnalyticsSnapshot

    def list_for_account(
        self, account_id: int, *, since: datetime | None = None, scope: str | None = None
    ) -> Sequence[AnalyticsSnapshot]:
        stmt = select(AnalyticsSnapshot).where(AnalyticsSnapshot.instagram_account_id == account_id)
        if since is not None:
            stmt = stmt.where(AnalyticsSnapshot.captured_at >= since)
        if scope is not None:
            stmt = stmt.where(AnalyticsSnapshot.scope == scope)
        return self.session.scalars(stmt.order_by(AnalyticsSnapshot.captured_at)).all()


class SystemSettingRepository(BaseRepository[SystemSetting]):
    model = SystemSetting

    def get_value(self, key: str, default: Any = None) -> Any:
        row = self.session.get(SystemSetting, key)
        return row.value.get("value", default) if row else default

    def set_value(self, key: str, value: Any, description: str | None = None) -> SystemSetting:
        row = self.session.get(SystemSetting, key)
        if row is None:
            row = SystemSetting(key=key, value={"value": value}, description=description)
            self.session.add(row)
        else:
            row.value = {"value": value}
            if description is not None:
                row.description = description
        self.session.flush()
        return row
