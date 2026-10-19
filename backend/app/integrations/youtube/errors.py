"""YouTube Data API v3 exception definitions."""

from enum import StrEnum


class YouTubeErrorKind(StrEnum):
    AUTH = "auth"
    QUOTA_EXCEEDED = "quota_exceeded"
    NOT_FOUND = "not_found"
    NETWORK = "network"
    RATE_LIMIT = "rate_limit"
    INVALID_REQUEST = "invalid_request"
    UPLOAD_FAILED = "upload_failed"
    UNKNOWN = "unknown"


class YouTubeApiError(Exception):
    """Base class for YouTube Data API v3 errors."""

    def __init__(
        self,
        kind: YouTubeErrorKind,
        message: str,
        *,
        status_code: int | None = None,
        details: dict | None = None,
    ) -> None:
        super().__init__(f"[{kind.value}] {message}")
        self.kind = kind
        self.message = message
        self.status_code = status_code
        self.details = details or {}
