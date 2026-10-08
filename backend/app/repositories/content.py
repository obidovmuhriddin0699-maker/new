from collections.abc import Sequence
from datetime import datetime

from sqlalchemy import func, select

from app.models import (
    Approval,
    Content,
    ContentAsset,
    ContentPerformance,
    ContentSchedule,
    ContentVersion,
)
from app.models.enums import ApprovalDecision, ContentStatus, ContentType, ScheduleStatus
from app.repositories.base import BaseRepository


class ContentRepository(BaseRepository[Content]):
    model = Content

    def search(
        self,
        *,
        status: ContentStatus | None = None,
        content_type: ContentType | None = None,
        offset: int = 0,
        limit: int = 50,
    ) -> tuple[Sequence[Content], int]:
        stmt = self._select()
        if status is not None:
            stmt = stmt.where(Content.status == status)
        if content_type is not None:
            stmt = stmt.where(Content.content_type == content_type)
        total = self.session.scalar(select(func.count()).select_from(stmt.subquery())) or 0
        rows = self.session.scalars(
            stmt.order_by(Content.created_at.desc(), Content.id.desc()).offset(offset).limit(limit)
        ).all()
        return rows, total


class ContentVersionRepository(BaseRepository[ContentVersion]):
    """Append-only: no update/delete helpers on purpose."""

    model = ContentVersion

    def get_version(self, content_id: int, version: int) -> ContentVersion | None:
        return self.session.scalar(
            select(ContentVersion).where(
                ContentVersion.content_id == content_id, ContentVersion.version == version
            )
        )

    def list_for_content(self, content_id: int) -> Sequence[ContentVersion]:
        return self.session.scalars(
            select(ContentVersion)
            .where(ContentVersion.content_id == content_id)
            .order_by(ContentVersion.version)
        ).all()


class ContentAssetRepository(BaseRepository[ContentAsset]):
    model = ContentAsset

    def list_for_content(self, content_id: int) -> Sequence[ContentAsset]:
        return self.session.scalars(
            self._select()
            .where(ContentAsset.content_id == content_id)
            .order_by(ContentAsset.position, ContentAsset.id)
        ).all()


class ContentScheduleRepository(BaseRepository[ContentSchedule]):
    model = ContentSchedule

    def get_by_idempotency_key(self, key: str) -> ContentSchedule | None:
        return self.session.scalar(
            select(ContentSchedule).where(ContentSchedule.idempotency_key == key)
        )

    def list_pending_for_content(self, content_id: int) -> Sequence[ContentSchedule]:
        return self.session.scalars(
            select(ContentSchedule).where(
                ContentSchedule.content_id == content_id,
                ContentSchedule.status == ScheduleStatus.PENDING,
            )
        ).all()

    def list_due(self, now: datetime, limit: int = 20) -> Sequence[ContentSchedule]:
        return self.session.scalars(
            select(ContentSchedule)
            .where(
                ContentSchedule.status == ScheduleStatus.PENDING,
                ContentSchedule.scheduled_at <= now,
            )
            .order_by(ContentSchedule.scheduled_at)
            .limit(limit)
        ).all()

    def list_for_content(self, content_id: int) -> Sequence[ContentSchedule]:
        return self.session.scalars(
            select(ContentSchedule)
            .where(ContentSchedule.content_id == content_id)
            .order_by(ContentSchedule.id)
        ).all()


class ApprovalRepository(BaseRepository[Approval]):
    model = Approval

    def get_active_approval(self, content_id: int, version: int) -> Approval | None:
        return self.session.scalar(
            select(Approval).where(
                Approval.content_id == content_id,
                Approval.content_version == version,
                Approval.decision == ApprovalDecision.APPROVED,
                Approval.invalidated_at.is_(None),
            )
        )

    def list_active_for_content(self, content_id: int) -> Sequence[Approval]:
        return self.session.scalars(
            select(Approval).where(
                Approval.content_id == content_id,
                Approval.decision == ApprovalDecision.APPROVED,
                Approval.invalidated_at.is_(None),
            )
        ).all()

    def list_for_content(self, content_id: int) -> Sequence[Approval]:
        return self.session.scalars(
            select(Approval).where(Approval.content_id == content_id).order_by(Approval.id)
        ).all()


class ContentPerformanceRepository(BaseRepository[ContentPerformance]):
    model = ContentPerformance

    def get_for_content(self, content_id: int) -> ContentPerformance | None:
        return self.session.scalar(
            select(ContentPerformance).where(ContentPerformance.content_id == content_id)
        )
