from fastapi import APIRouter, Response

from app import __version__
from app.core.config import get_settings
from app.core.database import check_database
from app.core.redis import check_redis
from app.schemas.common import ComponentStatus, HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health(response: Response) -> HealthResponse:
    """Liveness + dependency status. Redis is optional in development."""
    settings = get_settings()
    db_ok, db_err = check_database()
    redis_ok, redis_err = check_redis()
    status = "ok" if db_ok else "degraded"
    if not db_ok:
        response.status_code = 503
    return HealthResponse(
        status=status,
        app=settings.app_name,
        version=__version__,
        environment=settings.app_env,
        components={
            "database": ComponentStatus(ok=db_ok, error=db_err),
            "redis": ComponentStatus(ok=redis_ok, error=redis_err),
        },
    )
