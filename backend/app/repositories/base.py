"""Generic SQLAlchemy repository.

Repositories only read/write rows; they never commit (transactions are owned
by the service layer via ``app.core.transaction.atomic``) and contain no
business rules. Soft-deleted rows are excluded by default.
"""

from collections.abc import Sequence
from typing import Any, Generic, TypeVar

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from app.models.base import Base, SoftDeleteMixin, utcnow

ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository(Generic[ModelT]):
    model: type[ModelT]

    def __init__(self, session: Session) -> None:
        self.session = session

    # --- query helpers -------------------------------------------------
    @property
    def _soft_delete(self) -> bool:
        return issubclass(self.model, SoftDeleteMixin)

    def _select(self, *, include_deleted: bool = False) -> Select[tuple[ModelT]]:
        stmt = select(self.model)
        if self._soft_delete and not include_deleted:
            stmt = stmt.where(self.model.deleted_at.is_(None))  # type: ignore[attr-defined]
        return stmt

    # --- reads ---------------------------------------------------------
    def get(self, id_: Any, *, include_deleted: bool = False) -> ModelT | None:
        obj = self.session.get(self.model, id_)
        if obj is None:
            return None
        if self._soft_delete and not include_deleted and obj.deleted_at is not None:  # type: ignore[attr-defined]
            return None
        return obj

    def get_for_update(self, id_: Any) -> ModelT | None:
        """Row-level lock (``SELECT ... FOR UPDATE``) on PostgreSQL; no-op on SQLite."""
        pk = self.model.__mapper__.primary_key[0]
        stmt = self._select().where(pk == id_).with_for_update()
        return self.session.scalars(stmt).first()

    def list(
        self,
        *,
        offset: int = 0,
        limit: int = 50,
        order_by: Any = None,
        include_deleted: bool = False,
        **filters: Any,
    ) -> Sequence[ModelT]:
        stmt = self._select(include_deleted=include_deleted).filter_by(**filters)
        if order_by is not None:
            stmt = stmt.order_by(order_by)
        return self.session.scalars(stmt.offset(offset).limit(limit)).all()

    def count(self, *, include_deleted: bool = False, **filters: Any) -> int:
        stmt = self._select(include_deleted=include_deleted).filter_by(**filters)
        return self.session.scalar(select(func.count()).select_from(stmt.subquery())) or 0

    # --- writes --------------------------------------------------------
    def add(self, obj: ModelT) -> ModelT:
        self.session.add(obj)
        self.session.flush()
        return obj

    def soft_delete(self, obj: ModelT) -> None:
        if not self._soft_delete:
            raise TypeError(f"{self.model.__name__} does not support soft delete")
        obj.deleted_at = utcnow()  # type: ignore[attr-defined]
        self.session.flush()
