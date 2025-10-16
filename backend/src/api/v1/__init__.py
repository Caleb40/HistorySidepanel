from fastapi import APIRouter

from src.api.v1.routes.health import router as health_check

router = APIRouter(prefix="/v1")

router.include_router(health_check)
