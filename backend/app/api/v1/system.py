from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel

from app.api.deps import CurrentUser, DbSession, HumanActorDep
from app.core.errors import PermissionDeniedError
from app.providers.ai.factory import create_ai_provider
from app.schemas.ai import AIStatusResponse
from app.schemas.errors import error_responses
from app.services.guards import WRITER_ROLES, require_active_human
from app.services.ops import OpsMonitor

router = APIRouter(prefix="/system", tags=["system"])


@router.get("/ai-status", response_model=AIStatusResponse)
async def ai_status(_: CurrentUser) -> AIStatusResponse:
    """Reports whether the configured LLM is reachable. Never raises if Ollama is down."""
    provider = create_ai_provider()
    try:
        status = await provider.health()
    finally:
        await provider.aclose()
    return AIStatusResponse(
        provider=status.provider,
        model=status.model,
        available=status.available,
        model_installed=status.model_installed,
        error_code=status.error_code,
        message=status.message,
    )


class OpsProblemRead(BaseModel):
    key: str
    severity: Literal["critical", "warning"]
    message: str


class OpsStatusRead(BaseModel):
    ok: bool
    problems: list[OpsProblemRead]


@router.get(
    "/ops-status",
    response_model=OpsStatusRead,
    summary="Operational problems (owners and admins)",
    description="Live, read-only view of what the ops monitor checks. Does not send alerts.",
    responses=error_responses(401, 403),
)
def ops_status(db: DbSession, actor: HumanActorDep) -> OpsStatusRead:
    user = require_active_human(db, actor)
    if user.role not in WRITER_ROLES:
        raise PermissionDeniedError("Only owners and admins can see system status")
    problems = OpsMonitor(db).problems()
    return OpsStatusRead(
        ok=not problems,
        problems=[
            OpsProblemRead(key=p.key, severity=p.severity, message=p.message) for p in problems
        ],
    )
