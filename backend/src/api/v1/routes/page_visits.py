import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.params import Query
from sqlalchemy.ext.asyncio.session import AsyncSession
from src.api.v1.services.page_visit_service import PageVisitService
from src.core.db.database import async_get_db
from src.models.page_visit import PageVisit
from src.schemas.page_visit import VisitCreate, VisitResponse, StatsResponse

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post(
    "/visits",
    response_model=VisitResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Record a page visit",
    description="Store metrics for a visited webpage including detailed link and image analysis"
)
async def create_visit(
        visit: VisitCreate,
        db: AsyncSession = Depends(async_get_db)
):
    """Create a new page visit record"""
    service = PageVisitService(db)
    db_visit = await service.create_visit(visit)

    logger.info(
        f"Visit recorded for {visit.url} with "
        f"{visit.link_count} links ({visit.internal_links or 0} internal, {visit.external_links or 0} external), "
        f"{visit.word_count} words, "
        f"{visit.image_count} images ({visit.content_images or 0} content, {visit.decorative_images or 0} decorative)"
    )

    return db_visit


@router.get(
    "/visits",
    response_model=List[VisitResponse],
    summary="Get visits by URL",
    description="Retrieve all visit records for a specific URL, ordered by most recent first"
)
async def get_visits_by_url(
        url: str = Query(..., description="URL to filter visits by"),
        db: AsyncSession = Depends(async_get_db)
):
    """Get all visits for a specific URL"""
    service = PageVisitService(db)
    visits = await service.get_visits_by_url(url)
    logger.info(f"Retrieved {len(visits)} visits for {url}")
    return visits


@router.get(
    "/visits/latest",
    response_model=VisitResponse,
    summary="Get latest visit for URL",
    description="Retrieve the most recent visit record for a specific URL"
)
async def get_latest_visit(
        url: str = Query(..., description="URL to filter visits by"),
        db: AsyncSession = Depends(async_get_db)
):
    """Get the most recent visit for a specific URL"""
    service = PageVisitService(db)
    visit = await service.get_latest_visit(url)

    if not visit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No visits found for this URL"
        )

    logger.info(f"Retrieved latest visit for {url}")
    return visit


@router.get(
    "/visits/stats",
    response_model=StatsResponse,
    summary="Get overall statistics",
    description="Retrieve aggregated statistics about all recorded visits"
)
async def get_visit_stats(db: AsyncSession = Depends(async_get_db)):
    """Get overall statistics about visits"""
    service = PageVisitService(db)
    stats = await service.get_visit_stats()

    logger.info(f"Retrieved stats: {stats['total_visits']} visits, {stats['unique_urls']} unique URLs")
    return stats


@router.get(
    "/visits/recent",
    response_model=List[VisitResponse],
    summary="Get recent visits",
    description="Retrieve the most recent visits across all URLs"
)
async def get_recent_visits(
        limit: int = Query(10, ge=1, le=100),
        db: AsyncSession = Depends(async_get_db)
):
    """Get the most recent visits across all URLs"""
    service = PageVisitService(db)
    visits = await service.get_recent_visits(limit)

    logger.info(f"Retrieved {len(visits)} recent visits")
    return visits
