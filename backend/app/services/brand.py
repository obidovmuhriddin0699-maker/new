from collections.abc import Sequence
from typing import Any

from sqlalchemy.orm import Session

from app.core.actors import Actor
from app.core.errors import AppError, ConflictError, NotFoundError
from app.core.transaction import atomic
from app.models import BrandProfile
from app.models.enums import AuditAction
from app.repositories import BrandProfileRepository
from app.services.audit import AuditLogService
from app.services.guards import require_human_writer

BRAND_FIELDS = frozenset(
    {"name", "niche", "voice", "topics", "forbidden_rules", "languages", "visual_style"}
)


class BrandProfileService:
    """Brand voice/rules are owned by humans; agents only read them."""

    def __init__(self, session: Session, audit: AuditLogService | None = None) -> None:
        self.session = session
        self.audit = audit or AuditLogService(session)
        self.repo = BrandProfileRepository(session)

    def get(self, profile_id: int) -> BrandProfile:
        profile = self.repo.get(profile_id)
        if profile is None:
            raise NotFoundError("Brand profile not found")
        return profile

    def get_default(self) -> BrandProfile | None:
        return self.repo.get_default()

    def list(self) -> Sequence[BrandProfile]:
        return self.repo.list(order_by=BrandProfile.id)

    def create(self, actor: Actor, *, make_default: bool = False, **fields: Any) -> BrandProfile:
        with atomic(self.session):
            require_human_writer(self.session, actor)
            self._validate(fields)
            if self.repo.get_by_name(fields["name"]):
                raise ConflictError("A brand profile with this name already exists")
            profile = BrandProfile(**fields)
            self.repo.add(profile)
            if make_default:
                self._set_default(profile)
            self.audit.record(
                AuditAction.BRAND_PROFILE_CREATED,
                actor,
                details={"brand_profile_id": profile.id, "name": profile.name},
            )
            return profile

    def update(self, profile_id: int, actor: Actor, **changes: Any) -> BrandProfile:
        with atomic(self.session):
            require_human_writer(self.session, actor)
            self._validate(changes)
            profile = self.get(profile_id)
            for name, value in changes.items():
                setattr(profile, name, value)
            self.session.flush()
            self.audit.record(
                AuditAction.BRAND_PROFILE_UPDATED,
                actor,
                details={"brand_profile_id": profile.id, "fields": sorted(changes)},
            )
            return profile

    def set_default(self, profile_id: int, actor: Actor) -> BrandProfile:
        with atomic(self.session):
            require_human_writer(self.session, actor)
            profile = self.get(profile_id)
            self._set_default(profile)
            return profile

    def _set_default(self, profile: BrandProfile) -> None:
        for other in self.repo.list(limit=1000):
            other.is_default = other.id == profile.id
        self.session.flush()

    @staticmethod
    def _validate(fields: dict[str, Any]) -> None:
        unknown = set(fields) - BRAND_FIELDS
        if unknown:
            raise AppError(f"Unknown brand fields: {sorted(unknown)}", code="invalid_fields")
