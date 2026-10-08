from typing import Any

from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    code: str = Field(examples=["version_mismatch"])
    message: str = Field(examples=["Content changed since you reviewed it"])
    details: Any | None = None
    request_id: str | None = None


class ErrorResponse(BaseModel):
    error: ErrorDetail


def error_responses(*codes: int) -> dict[int | str, dict[str, Any]]:
    descriptions = {
        400: "Bad request",
        401: "Not authenticated or session expired",
        403: "Authenticated but not allowed (role, or non-human actor)",
        404: "Resource not found",
        409: "Conflict: invalid state transition, version mismatch or missing approval",
        422: "Request validation failed",
    }
    return {c: {"model": ErrorResponse, "description": descriptions[c]} for c in codes}
