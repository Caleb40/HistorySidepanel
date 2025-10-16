import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio.session import AsyncSession

from src.core.db.database import async_get_db
from src.models.page_visit import PageVisit
from src.schemas.page_visit import VisitCreate, VisitResponse

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
