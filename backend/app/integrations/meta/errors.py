"""Map Meta API errors to stable kinds and user-friendly Uzbek messages.

Two error shapes exist:
* Graph API:  {"error": {"message", "type", "code", "error_subcode", "fbtrace_id"}}
* OAuth host: {"error_type": "OAuthException", "code": 400, "error_message": "..."}
Messages never include tokens; only Meta's own message (truncated) and fbtrace_id.
"""

from enum import StrEnum
from typing import Any

from fastapi import status

from app.core.errors import AppError


class MetaErrorKind(StrEnum):
    OAUTH = "oauth"
    TOKEN_EXPIRED = "token_expired"  # noqa: S105
    PERMISSION_DENIED = "permission_denied"
    RATE_LIMIT = "rate_limit"
    INVALID_REQUEST = "invalid_request"
    MEDIA_VALIDATION = "media_validation"
    PUBLISHING_FAILED = "publishing_failed"
    TRANSIENT = "transient"
    NETWORK = "network"
    NOT_CONFIGURED = "not_configured"
    UNKNOWN = "unknown"


USER_MESSAGES = {
    MetaErrorKind.OAUTH: "Instagram avtorizatsiyasi muvaffaqiyatsiz. Qayta ulaning.",
    MetaErrorKind.TOKEN_EXPIRED: "Instagram tokeni muddati tugagan yoki bekor qilingan. "
    "Akkauntni qayta ulang.",
    MetaErrorKind.PERMISSION_DENIED: "Kerakli Instagram ruxsatlari berilmagan.",
    MetaErrorKind.RATE_LIMIT: "Meta API so‘rovlar limiti tugadi. Keyinroq urinib ko‘ring.",
    MetaErrorKind.INVALID_REQUEST: "Meta so‘rovni rad etdi (noto‘g‘ri parametr).",
    MetaErrorKind.MEDIA_VALIDATION: "Media Instagram talablariga mos emas.",
    MetaErrorKind.PUBLISHING_FAILED: "Instagram'ga nashr qilish muvaffaqiyatsiz bo‘ldi.",
    MetaErrorKind.TRANSIENT: "Meta serverida vaqtinchalik xato. Keyinroq urinib ko‘ring.",
    MetaErrorKind.NETWORK: "Meta API bilan aloqa o‘rnatib bo‘lmadi.",
    MetaErrorKind.NOT_CONFIGURED: "Meta ilovasi sozlanmagan (META_APP_ID, META_APP_SECRET, "
    "META_REDIRECT_URI).",
    MetaErrorKind.UNKNOWN: "Meta API noma’lum xato qaytardi.",
}

HTTP_STATUS = {
    MetaErrorKind.NOT_CONFIGURED: status.HTTP_503_SERVICE_UNAVAILABLE,
    MetaErrorKind.NETWORK: status.HTTP_503_SERVICE_UNAVAILABLE,
    MetaErrorKind.RATE_LIMIT: status.HTTP_429_TOO_MANY_REQUESTS,
    MetaErrorKind.PERMISSION_DENIED: status.HTTP_403_FORBIDDEN,
}


class MetaApiError(AppError):
    def __init__(
        self,
        kind: MetaErrorKind,
        *,
        meta_message: str | None = None,
        meta_code: int | None = None,
        meta_subcode: int | None = None,
        fbtrace_id: str | None = None,
    ) -> None:
        details: dict[str, Any] = {"kind": kind.value}
        if meta_code is not None:
            details["meta_code"] = meta_code
        if meta_subcode is not None:
            details["meta_subcode"] = meta_subcode
        if fbtrace_id:
            details["fbtrace_id"] = fbtrace_id
        if meta_message:
            details["meta_message"] = meta_message[:300]
        super().__init__(USER_MESSAGES[kind], details=details, code=f"meta_{kind.value}")
        self.kind = kind
        self.status_code = HTTP_STATUS.get(kind, status.HTTP_502_BAD_GATEWAY)


_RATE_LIMIT_CODES = {4, 17, 32, 613, 80001, 80002, 80006}
_EXPIRED_SUBCODES = {458, 459, 460, 463, 464, 467, 492}


def classify(code: int | None, subcode: int | None, error_type: str | None) -> MetaErrorKind:
    if subcode == 2207042:  # content publishing limit reached (24 h moving window)
        return MetaErrorKind.RATE_LIMIT
    if subcode is not None and 2207000 <= subcode <= 2207999:  # media/publishing errors
        return MetaErrorKind.MEDIA_VALIDATION
    if code == 190:
        return (
            MetaErrorKind.TOKEN_EXPIRED
            if subcode in _EXPIRED_SUBCODES or subcode is None
            else MetaErrorKind.OAUTH
        )
    if code in _RATE_LIMIT_CODES:
        return MetaErrorKind.RATE_LIMIT
    if code == 10 or (code is not None and 200 <= code <= 299):
        return MetaErrorKind.PERMISSION_DENIED
    if code in (1, 2):
        return MetaErrorKind.TRANSIENT
    if code in (9004, 36000, 36001, 36003, 36004, 2207026):
        return MetaErrorKind.MEDIA_VALIDATION
    if code == 100:
        return MetaErrorKind.INVALID_REQUEST
    if error_type == "OAuthException":
        return MetaErrorKind.OAUTH
    return MetaErrorKind.UNKNOWN


def from_response(status_code: int, body: Any) -> MetaApiError:
    if isinstance(body, dict) and isinstance(body.get("error"), dict):
        err = body["error"]
        code = _int(err.get("code"))
        sub = _int(err.get("error_subcode"))
        return MetaApiError(
            classify(code, sub, err.get("type")),
            meta_message=str(err.get("message") or ""),
            meta_code=code,
            meta_subcode=sub,
            fbtrace_id=err.get("fbtrace_id"),
        )
    if isinstance(body, dict) and ("error_type" in body or "error_message" in body):
        return MetaApiError(
            classify(_int(body.get("code")), None, body.get("error_type")),
            meta_message=str(body.get("error_message") or ""),
            meta_code=_int(body.get("code")),
        )
    if status_code >= 500:
        return MetaApiError(MetaErrorKind.TRANSIENT, meta_code=status_code)
    return MetaApiError(MetaErrorKind.UNKNOWN, meta_code=status_code)


def _int(value: Any) -> int | None:
    try:
        return int(value) if value is not None else None
    except (TypeError, ValueError):
        return None
