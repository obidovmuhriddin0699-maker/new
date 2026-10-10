"""Import every model so Base.metadata is complete (Alembic autogenerate relies on this)."""

from app.models.analytics import AnalyticsReport, AnalyticsSnapshot
from app.models.base import Base
from app.models.brand import BrandProfile
from app.models.content import (
    Approval,
    Content,
    ContentAsset,
    ContentPerformance,
    ContentSchedule,
    ContentVersion,
)
from app.models.instagram import InstagramAccount, OAuthToken
from app.models.system import (
    AIJob,
    AuditLog,
    DataDeletionRequest,
    OAuthState,
    SystemSetting,
    TelegramActionToken,
    TelegramLinkCode,
)
from app.models.user import RevokedToken, User

__all__ = [
    "AIJob",
    "AnalyticsReport",
    "AnalyticsSnapshot",
    "Approval",
    "AuditLog",
    "Base",
    "BrandProfile",
    "Content",
    "ContentAsset",
    "ContentPerformance",
    "ContentSchedule",
    "ContentVersion",
    "DataDeletionRequest",
    "InstagramAccount",
    "OAuthState",
    "OAuthToken",
    "RevokedToken",
    "SystemSetting",
    "TelegramActionToken",
    "TelegramLinkCode",
    "User",
]
