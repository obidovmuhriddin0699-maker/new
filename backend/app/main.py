from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
import logging
import os
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import Engine, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker

from backend.app import models  # noqa: F401
from backend.app.config import cors_origins, is_production, validate_production_configuration
from backend.app.database import Base, engine
from backend.app.routers import ai, auth, billing, orchestrator, telegram, workspaces


logger = logging.getLogger(__name__)


def create_app(
    database_engine: Engine = engine,
    frontend_dist_dir: Path | None = None,
) -> FastAPI:
    frontend_dir = frontend_dist_dir or Path(
        os.getenv("FRONTEND_DIST_DIR", str(Path(__file__).resolve().parents[2] / "frontend_dist"))
    )
    frontend_index = frontend_dir / "index.html"

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        if is_production(os.environ):
            validate_production_configuration(
                os.environ,
                database_engine.url.drivername,
            )
        else:
            Base.metadata.create_all(bind=database_engine)
        yield

    app = FastAPI(title="Local AI SaaS API", lifespan=lifespan)
    app.state.engine = database_engine
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins(os.environ),
        allow_credentials=True,
        allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type", "X-CSRF-Token"],
    )
    app.state.session_factory = sessionmaker(
        bind=database_engine,
        autoflush=False,
        autocommit=False,
    )
    app.include_router(auth.router)
    app.include_router(ai.router)
    app.include_router(billing.router)
    app.include_router(orchestrator.router)
    app.include_router(telegram.router)
    app.include_router(workspaces.router)
    assets_dir = frontend_dir / "assets"
    if assets_dir.is_dir():
        app.mount(
            "/assets",
            StaticFiles(directory=assets_dir),
            name="frontend-assets",
        )

    @app.get("/", response_model=None)
    def read_root() -> Response:
        if frontend_index.is_file():
            return FileResponse(frontend_index)
        return JSONResponse({"message": "Local AI SaaS API"})

    @app.get("/health")
    def health_check() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/ready")
    def readiness_check(request: Request) -> dict[str, str]:
        try:
            with request.app.state.engine.connect() as connection:
                connection.execute(text("SELECT 1"))
        except SQLAlchemyError as exc:
            logger.error("Database readiness check failed (%s)", type(exc).__name__)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database is unavailable",
            ) from exc
        return {"status": "ready"}

    return app


app = create_app()
