from fastapi import APIRouter

from app.api.health import health
from app.api.v1 import ai, approvals, auth, contents, panel, system, telegram

api_router = APIRouter()
api_router.add_api_route("/health", health, methods=["GET"], tags=["health"])
api_router.include_router(auth.router)
api_router.include_router(system.router)
api_router.include_router(contents.router)
api_router.include_router(ai.router)
api_router.include_router(panel.router)
api_router.include_router(telegram.router)
api_router.include_router(approvals.router)
