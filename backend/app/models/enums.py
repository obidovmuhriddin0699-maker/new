"""Domain enums. Stored as strings (portable across PostgreSQL/SQLite)."""

from enum import StrEnum


class UserRole(StrEnum):
    OWNER = "OWNER"
    ADMIN = "ADMIN"
    VIEWER = "VIEWER"


class MetaLoginMode(StrEnum):
    INSTAGRAM = "instagram"
    FACEBOOK = "facebook"


class InstagramAccountType(StrEnum):
    BUSINESS = "BUSINESS"
    CREATOR = "CREATOR"
    UNKNOWN = "UNKNOWN"


class ContentType(StrEnum):
    POST = "POST"
    CAROUSEL = "CAROUSEL"
    REELS = "REELS"
    STORY = "STORY"


class ContentStatus(StrEnum):
    DRAFT = "DRAFT"
    GENERATING = "GENERATING"
    READY_FOR_REVIEW = "READY_FOR_REVIEW"
    EDIT_REQUESTED = "EDIT_REQUESTED"
    APPROVED = "APPROVED"
    SCHEDULED = "SCHEDULED"
    PUBLISHING = "PUBLISHING"
    PUBLISHED = "PUBLISHED"
    FAILED = "FAILED"
    REJECTED = "REJECTED"


class ContentLanguage(StrEnum):
    UZ = "uz"
    RU = "ru"
    EN = "en"


class AssetKind(StrEnum):
    IMAGE = "IMAGE"
    VIDEO = "VIDEO"


class ScheduleStatus(StrEnum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    DONE = "DONE"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class ApprovalDecision(StrEnum):
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    EDIT_REQUESTED = "EDIT_REQUESTED"


class ApprovalChannel(StrEnum):
    WEB = "WEB"
    TELEGRAM = "TELEGRAM"


class ActorType(StrEnum):
    HUMAN = "HUMAN"
    AGENT = "AGENT"
    SYSTEM = "SYSTEM"


class AIJobStatus(StrEnum):
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
