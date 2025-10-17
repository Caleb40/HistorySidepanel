import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.params import Query
from sqlalchemy import select, desc, func
from sqlalchemy.ext.asyncio.session import AsyncSession

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
    description="Store metrics for a visited webpage including link count, word count, and image count"
)
async def create_visit(
        visit: VisitCreate,
        db: AsyncSession = Depends(async_get_db)
):
    """Create a new page visit record"""
    try:

        db_visit = PageVisit(
            url=visit.url,
            link_count=visit.link_count,
            word_count=visit.word_count,
            image_count=visit.image_count,
        )

        db.add(db_visit)
        await db.commit()
        await db.refresh(db_visit)

        logger.info(
            f"Visit recorded for {visit.url} with {visit.link_count} links, {visit.word_count} words, {visit.image_count} images"
        )

        return db_visit

    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating visit: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create visit record"
        )


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
    try:
        result = await db.execute(
            select(PageVisit)
            .where(PageVisit.url == url)
            .order_by(desc(PageVisit.created_at))
        )
        visits = result.scalars().all()

        logger.info(f"Retrieved {len(visits)} visits for {url}")
        return visits

    except Exception as e:
        logger.error(f"Error retrieving visits: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve visits"
        )


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
    try:
        result = await db.execute(
            select(PageVisit)
            .where(PageVisit.url == url)
            .order_by(desc(PageVisit.created_at))
            .limit(1)
        )
        visit = result.scalar_one_or_none()

        if not visit:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No visits found for this URL"
            )

        logger.info(f"Retrieved latest visit for {url}")
        return visit

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving latest visit: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve latest visit"
        )


@router.get(
    "/visits/stats",
    response_model=StatsResponse,
    summary="Get overall statistics",
    description="Retrieve aggregated statistics about all recorded visits"
)
async def get_visit_stats(db: AsyncSession = Depends(async_get_db)):
    """Get overall statistics about visits"""
    try:
        # Total visits count
        total_result = await db.execute(select(func.count(PageVisit.id)))
        total_visits = total_result.scalar_one()

        # Unique URLs count
        unique_urls_result = await db.execute(
            select(func.count(func.distinct(PageVisit.url)))
        )
        unique_urls = unique_urls_result.scalar_one()

        # Average metrics
        avg_links_result = await db.execute(select(func.avg(PageVisit.link_count)))
        avg_links = round(avg_links_result.scalar_one() or 0, 2)

        avg_words_result = await db.execute(select(func.avg(PageVisit.word_count)))
        avg_words = round(avg_words_result.scalar_one() or 0, 2)

        avg_images_result = await db.execute(select(func.avg(PageVisit.image_count)))
        avg_images = round(avg_images_result.scalar_one() or 0, 2)

        return {
            "total_visits": total_visits,
            "unique_urls": unique_urls,
            "average_links": avg_links,
            "average_words": avg_words,
            "average_images": avg_images
        }

    except Exception as e:
        logger.error(f"Error retrieving stats: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve statistics"
        )


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
    try:
        result = await db.execute(
            select(PageVisit)
            .order_by(desc(PageVisit.created_at))
            .limit(limit)
        )
        visits = result.scalars().all()

        logger.info(f"Retrieved {len(visits)} recent visits")
        return visits

    except Exception as e:
        logger.error(f"Error retrieving recent visits: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve recent visits"
        )
