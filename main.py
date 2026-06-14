from contextlib import asynccontextmanager
from fastapi import FastAPI

from api.v1.router import api_router
from core.config import settings
from db.session import engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: nothing needed for NeonDB / external managed DB
    yield
    # Shutdown: dispose connection pool cleanly
    await engine.dispose()


def create_app() -> FastAPI:
    app = FastAPI(
        title="Todos API",
        version="1.0.0",
        docs_url="/docs" if settings.is_dev else None,
        redoc_url="/redoc" if settings.is_dev else None,
        lifespan=lifespan,
    )
    app.include_router(api_router)
    return app


app = create_app()
