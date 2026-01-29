"""FastAPI application factory."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.errors import install_error_handlers
from api.routers.v1 import router as v1_router
from config.settings import settings


def create_app() -> FastAPI:
    """Create FastAPI app instance."""
    fastapi_app = FastAPI(
        title="EMK Tender API",
        version="0.1.0",
        docs_url=f"{settings.api.prefix}/docs",
        openapi_url=f"{settings.api.prefix}/openapi.json",
    )

    if getattr(settings, "cors", None) and settings.cors.enabled:
        fastapi_app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.cors.origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    install_error_handlers(fastapi_app)

    fastapi_app.include_router(v1_router, prefix=settings.api.prefix)

    return fastapi_app


app = create_app()
