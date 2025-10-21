import pytest

from src.api.v1.services.page_visit_service import PageVisitService
from src.models.page_visit import PageVisit
from src.schemas.page_visit import VisitCreate


@pytest.mark.asyncio
async def test_create_visit(db_session):
    service = PageVisitService(db_session)
    data = VisitCreate(
        url="https://example.com",
        link_count=10,
        internal_links=6,
        external_links=4,
        word_count=500,
        image_count=8,
        content_images=6,
        decorative_images=2
    )

    visit = await service.create_visit(data)
    assert isinstance(visit, PageVisit)
    assert visit.url == "https://example.com"


@pytest.mark.asyncio
async def test_get_visits_by_url(db_session):
    service = PageVisitService(db_session)
    url = "https://test.com"

    for i in range(2):
        await service.create_visit(VisitCreate(
            url=url,
            link_count=5,
            internal_links=2,
            external_links=3,
            word_count=100,
            image_count=1,
            content_images=1,
            decorative_images=0
        ))

    visits = await service.get_visits_by_url(url)
    assert len(visits) == 2
    assert all(v.url == url for v in visits)


@pytest.mark.asyncio
async def test_get_latest_visit(db_session):
    service = PageVisitService(db_session)
    url = "https://latest.com"
    await service.create_visit(VisitCreate(
        url=url,
        link_count=3,
        internal_links=1,
        external_links=2,
        word_count=50,
        image_count=2,
        content_images=1,
        decorative_images=1
    ))

    visit = await service.get_latest_visit(url)
    assert visit.url == url


@pytest.mark.asyncio
async def test_get_visit_stats(db_session):
    service = PageVisitService(db_session)
    stats = await service.get_visit_stats()
    assert "total_visits" in stats
    assert isinstance(stats["total_visits"], int)


@pytest.mark.asyncio
async def test_get_recent_visits(db_session):
    service = PageVisitService(db_session)
    visits = await service.get_recent_visits()
    assert isinstance(visits, list)
