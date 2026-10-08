"""Import every model so Base.metadata is complete (Alembic autogenerate relies on this)."""

from app.models.analytics import AnalyticsSnapshot
from app.models.base import Base
from app.models.brand import BrandProfile
from app.models.content import (
    Approval,
    Content,
    ContentAsset,
    ContentPerformance,
    ContentSchedule,
)
from app.models.instagram import InstagramAccount, OAuthToken
from app.models.system import AIJob, AuditLog, SystemSetting
from app.models.user import User

__all__ = [
    "AIJob",
    "AnalyticsSnapshot",
    "Approval",
    "AuditLog",
    "Base",
    "BrandProfile",
    "Content",
    "ContentAsset",
    "ContentPerformance",
    "ContentSchedule",
    "InstagramAccount",
    "OAuthToken",
    "SystemSetting",
    "User",
]
