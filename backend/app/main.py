from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import Engine
from sqlalchemy.orm import sessionmaker

from backend.app import models  # noqa: F401
from backend.app.database import Base, engine
from backend.app.routers import ai, auth, billing, workspaces


def create_app(database_engine: Engine = engine) -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        Base.metadata.create_all(bind=database_engine)
        yield

    app = FastAPI(title="Local AI SaaS API", lifespan=lifespan)
    app.state.session_factory = sessionmaker(
        bind=database_engine,
        autoflush=False,
        autocommit=False,
    )
    app.include_router(auth.router)
    app.include_router(ai.router)
    app.include_router(billing.router)
    app.include_router(workspaces.router)

    @app.get("/")
    def read_root() -> dict[str, str]:
        return {"message": "Local AI SaaS API"}

    @app.get("/health")
    def health_check() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
