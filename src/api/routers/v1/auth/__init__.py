"""Auth router package."""

from fastapi import APIRouter

from . import routes

router = APIRouter(prefix="/auth", tags=["auth"])
router.include_router(routes.router)

__all__ = ["router"]
