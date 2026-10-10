from typing import Literal

from pydantic import BaseModel


class ComponentStatus(BaseModel):
    ok: bool
    error: str | None = None


class HealthResponse(BaseModel):
    status: Literal["ok", "degraded"]
    app: str
    version: str
    environment: str
    components: dict[str, ComponentStatus]
