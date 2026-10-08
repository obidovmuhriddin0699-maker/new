from fastapi import APIRouter

from app.api.deps import CurrentUser
from app.providers.ai.factory import create_ai_provider
from app.schemas.ai import AIStatusResponse

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
