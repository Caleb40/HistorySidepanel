from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func
from typing import List, Optional

from backend.src.models.page_visit import PageVisit
from backend.src.schemas.page_visit import VisitCreate


class PageVisitService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_visit(self, visit_data: VisitCreate) -> PageVisit:
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
        return db_visit

    async def get_visits_by_url(self, url: str) -> List[PageVisit]:
        result = await self.db.execute(
            select(PageVisit)
            .where(PageVisit.url == url)
            .order_by(desc(PageVisit.created_at))
        )
        return result.scalars().all()

    async def get_latest_visit(self, url: str) -> Optional[PageVisit]:
        result = await self.db.execute(
            select(PageVisit)
            .where(PageVisit.url == url)
            .order_by(desc(PageVisit.created_at))
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def get_visit_stats(self):
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