"""API v1 router."""

from fastapi import APIRouter

from api.routers.v1.auth import router as auth
from api.routers.v1.example import router as example

router = APIRouter()
router.include_router(auth)
router.include_router(example)

__all__ = ["router"]
