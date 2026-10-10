"""FastAPI application factory."""

import logging
import re
import time
import uuid
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse

from app import __version__
from app.api.health import router as health_router
from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.errors import AppError, error_body, register_exception_handlers
from app.core.logging import configure_logging, request_id_var
from app.core.ratelimit import API_IP, client_ip, get_limiter
from app.providers.ai.base import AIProviderError

logger = logging.getLogger("app")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    logger.info(
        "startup",
        extra={
            "environment": settings.app_env,
            "database": "sqlite" if settings.is_sqlite else "postgresql",
            "ai_provider": settings.ai_provider,
            "ai_model": settings.ai_model,
            "meta_dry_run": settings.meta_dry_run,
        },
    )
    yield
    logger.info("shutdown")


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings.log_level, settings.log_json)

    app = FastAPI(
        title=settings.app_name,
        version=__version__,
        debug=settings.debug,
        lifespan=lifespan,
        docs_url="/docs" if settings.app_env != "production" else None,
        redoc_url=None,
        openapi_url="/openapi.json" if settings.app_env != "production" else None,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
        expose_headers=["X-Request-ID"],
    )

    if settings.allowed_hosts:
        app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.allowed_hosts)

    upload_limit = max(settings.media_max_image_mb, settings.media_max_video_mb) * 1024 * 1024
    json_limit = settings.max_json_body_kb * 1024

    @app.middleware("http")
    async def request_context(request: Request, call_next) -> Response:  # type: ignore[no-untyped-def]
        incoming = request.headers.get("X-Request-ID", "")
        # Only a safe charset is echoed back and logged (no header/log injection).
        request_id = incoming if _REQUEST_ID.fullmatch(incoming) else uuid.uuid4().hex
        token = request_id_var.set(request_id)
        start = time.perf_counter()
        try:
            response = await _guard(request) or await call_next(request)
        except Exception:
            # Handled here (not by ServerErrorMiddleware) so the request ID is preserved.
            logger.exception("unhandled_error", extra={"path": request.url.path})
            response = JSONResponse(
                status_code=500, content=error_body("internal_error", "Internal server error")
            )
        finally:
            request_id_var.reset(token)
        response.headers["X-Request-ID"] = request_id
        _security_headers(request, response, production=settings.app_env == "production")
        logger.info(
            "request",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": round((time.perf_counter() - start) * 1000, 1),
            },
        )
        return response

    async def _guard(request: Request) -> Response | None:
        """Cheap checks before routing: declared body size and the global per-IP limit."""
        path = request.url.path
        if request.method in ("POST", "PUT", "PATCH"):
            limit = upload_limit if path.endswith("/assets/upload") else json_limit
            try:
                length = int(request.headers.get("content-length") or 0)
            except ValueError:
                length = limit + 1
            if length > limit:
                return JSONResponse(
                    status_code=413,
                    content=error_body("body_too_large", "Request body too large"),
                )
        if path.startswith(settings.api_v1_prefix) and not path.endswith("/health"):
            allowed, retry = get_limiter().hit(API_IP, f"ip:{client_ip(request)}")
            if not allowed:
                return JSONResponse(
                    status_code=429,
                    content=error_body("rate_limited", API_IP.message),
                    headers={"Retry-After": str(retry)},
                )
        return None

    register_exception_handlers(app)

    @app.exception_handler(AIProviderError)
    async def _ai_error(request: Request, exc: AIProviderError) -> Response:
        from app.core.errors import ServiceUnavailableError

        handler = app.exception_handlers[AppError]
        return await handler(request, ServiceUnavailableError(exc.message, code=exc.code))

    app.include_router(health_router)
    app.include_router(api_router, prefix=settings.api_v1_prefix)
    return app


_REQUEST_ID = re.compile(r"[A-Za-z0-9._-]{1,64}")
_API_CSP = "default-src 'none'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'"


def _security_headers(request: Request, response: Response, *, production: bool) -> None:
    h = response.headers
    h["X-Content-Type-Options"] = "nosniff"
    h["X-Frame-Options"] = "DENY"
    h["Referrer-Policy"] = "no-referrer"
    h["Permissions-Policy"] = "camera=(), microphone=(), geolocation=(), payment=()"
    h["Cross-Origin-Opener-Policy"] = "same-origin"
    path = request.url.path
    if "/media/" in path:
        # Meta's servers (and the panel) fetch uploaded media; the files are inert bytes.
        h["Cross-Origin-Resource-Policy"] = "cross-origin"
    else:
        h["Cross-Origin-Resource-Policy"] = "same-origin"
        h.setdefault("Cache-Control", "no-store")
    if not path.startswith("/docs"):
        h["Content-Security-Policy"] = _API_CSP
    if production:
        h["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"


app = create_app()
