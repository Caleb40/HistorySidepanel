from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, ConfigDict


class VisitCreate(BaseModel):
    url: str = Field(..., description="The URL of the visited page")
    link_count: int = Field(..., ge=0, description="Number of links on the page")
    internal_links: Optional[int] = Field(None, ge=0, description="Number of internal links")
    external_links: Optional[int] = Field(None, ge=0, description="Number of external links")
    word_count: int = Field(..., ge=0, description="Number of words on the page")
    image_count: int = Field(..., ge=0, description="Number of images on the page")
    content_images: Optional[int] = Field(None, ge=0, description="Number of content images")
    decorative_images: Optional[int] = Field(None, ge=0, description="Number of decorative images")
    datetime_visited: Optional[datetime] = Field(None, description="When the visit occurred")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "url": "https://example.com",
                "link_count": 25,
                "internal_links": 20,
                "external_links": 5,
                "word_count": 1500,
                "image_count": 8,
                "content_images": 6,
                "decorative_images": 2
            }
        }
    )


class VisitResponse(BaseModel):
    id: int
    url: str
    link_count: int
    internal_links: Optional[int] = None
    external_links: Optional[int] = None
    word_count: int
    image_count: int
    content_images: Optional[int] = None
    decorative_images: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PaginatedVisitsResponse(BaseModel):
    items: List[VisitResponse]
    total: int
    page: int
    items_per_page: int

    model_config = ConfigDict(from_attributes=True)


class StatsResponse(BaseModel):
    total_visits: int
    unique_urls: int
    average_links: float
    average_internal_links: Optional[float] = None
    average_external_links: Optional[float] = None
    average_words: float
    average_images: float
    average_content_images: Optional[float] = None
    average_decorative_images: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)
