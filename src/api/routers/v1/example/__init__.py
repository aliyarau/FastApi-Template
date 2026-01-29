from fastapi import APIRouter

from api.routers.v1.example.example_of_protected_route import router as example

router = APIRouter(tags=['example'])
router.include_router(example)
