from fastapi import APIRouter

from src.api.v1.routes.health import router as health_check
from src.api.v1.routes.page_visits import router as page_visits

router = APIRouter(prefix="/v1")

router.include_router(health_check)
router.include_router(page_visits)
