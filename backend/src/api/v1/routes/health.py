from fastapi import APIRouter
from starlette.requests import Request

router = APIRouter(tags=["health"])


@router.get("/health", include_in_schema=False)
async def health_check(request: Request) -> str:
    return "OK"
