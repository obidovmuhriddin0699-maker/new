from fastapi import APIRouter

from app.api.health import health
from app.api.v1 import auth, contents, system

api_router = APIRouter()
api_router.add_api_route("/health", health, methods=["GET"], tags=["health"])
api_router.include_router(auth.router)
api_router.include_router(system.router)
api_router.include_router(contents.router)
