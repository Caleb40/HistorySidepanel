import logging
from typing import List, Optional

from sqlalchemy import select, desc, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.page_visit import PageVisit
from src.schemas.page_visit import VisitCreate

logger = logging.getLogger(__name__)


class PageVisitService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_visit(self, visit_data: VisitCreate) -> PageVisit:
        """Create a new page visit record"""
        try:
            db_visit = PageVisit(
                url=visit_data.url,
                link_count=visit_data.link_count,
                internal_links=visit_data.internal_links,
                external_links=visit_data.external_links,
                word_count=visit_data.word_count,
                image_count=visit_data.image_count,
                content_images=visit_data.content_images,
                decorative_images=visit_data.decorative_images
            )

            self.db.add(db_visit)
            await self.db.commit()
            await self.db.refresh(db_visit)

            logger.info(
                f"Visit recorded for {visit_data.url} with "
                f"{visit_data.link_count} links, {visit_data.word_count} words, "
                f"{visit_data.image_count} images"
            )

            return db_visit

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Database error creating visit: {str(e)}", exc_info=True)
            # Let the global exception handler deal with it
            raise

    async def get_visits_by_url(self, url: str) -> List[PageVisit]:
        """Get all visits for a specific URL"""
        try:
            result = await self.db.execute(
                select(PageVisit)
                .where(PageVisit.url == url)
                .order_by(desc(PageVisit.created_at))
            )
            visits = result.scalars().all()

            logger.info(f"Retrieved {len(visits)} visits for {url}")
            return visits

        except Exception as e:
            logger.error(f"Database error retrieving visits: {str(e)}", exc_info=True)
            # Let the global exception handler deal with it
            raise

    async def get_latest_visit(self, url: str) -> Optional[PageVisit]:
        """Get the most recent visit for a specific URL"""
        try:
            result = await self.db.execute(
                select(PageVisit)
                .where(PageVisit.url == url)
                .order_by(desc(PageVisit.created_at))
                .limit(1)
            )
            visit = result.scalar_one_or_none()

            logger.info(f"Retrieved latest visit for {url}")
            return visit

        except Exception as e:
            logger.error(f"Database error retrieving latest visit: {str(e)}", exc_info=True)
            # Let the global exception handler deal with it
            raise

    async def get_visit_stats(self) -> dict:
        """Get overall statistics about visits"""
        try:
            stats_query = select(
                func.count(PageVisit.id).label('total_visits'),
                func.count(func.distinct(PageVisit.url)).label('unique_urls'),
                func.round(func.avg(PageVisit.link_count), 2).label('average_links'),
                func.round(func.avg(PageVisit.internal_links), 2).label('average_internal_links'),
                func.round(func.avg(PageVisit.external_links), 2).label('average_external_links'),
                func.round(func.avg(PageVisit.word_count), 2).label('average_words'),
                func.round(func.avg(PageVisit.image_count), 2).label('average_images'),
                func.round(func.avg(PageVisit.content_images), 2).label('average_content_images'),
                func.round(func.avg(PageVisit.decorative_images), 2).label('average_decorative_images')
            )

            result = await self.db.execute(stats_query)
            stats = result.first()

            return {
                "total_visits": stats.total_visits or 0,
                "unique_urls": stats.unique_urls or 0,
                "average_links": float(stats.average_links or 0),
                "average_internal_links": float(stats.average_internal_links or 0),
                "average_external_links": float(stats.average_external_links or 0),
                "average_words": float(stats.average_words or 0),
                "average_images": float(stats.average_images or 0),
                "average_content_images": float(stats.average_content_images or 0),
                "average_decorative_images": float(stats.average_decorative_images or 0)
            }

        except Exception as e:
            logger.error(f"Database error retrieving stats: {str(e)}", exc_info=True)
            # Let the global exception handler deal with it
            raise

    async def get_recent_visits(self, limit: int = 10) -> List[PageVisit]:
        """Get the most recent visits across all URLs"""
        try:
            result = await self.db.execute(
                select(PageVisit)
                .order_by(desc(PageVisit.created_at))
                .limit(limit)
            )
            visits = result.scalars().all()

            logger.info(f"Retrieved {len(visits)} recent visits")
            return visits

        except Exception as e:
            logger.error(f"Database error retrieving recent visits: {str(e)}", exc_info=True)
            # Let the global exception handler deal with it
            raise
