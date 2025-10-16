from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class VisitCreate(BaseModel):
    url: str = Field(..., description="The URL of the visited page")
    link_count: int = Field(..., ge=0, description="Number of links on the page")
    word_count: int = Field(..., ge=0, description="Number of words on the page")
    image_count: int = Field(..., ge=0, description="Number of images on the page")
    datetime_visited: Optional[datetime] = Field(None, description="When the visit occurred")

    class Config:
        json_schema_extra = {
            "example": {
                "url": "https://example.com",
                "link_count": 25,
                "word_count": 1500,
                "image_count": 8
            }
        }


class VisitResponse(BaseModel):
    id: int
    url: str
    link_count: int
    word_count: int
    image_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PaginatedVisitsResponse(BaseModel):
    items: List[VisitResponse]
    total: int
    page: int
    items_per_page: int


class StatsResponse(BaseModel):
    total_visits: int
    unique_urls: int
    average_links: float
    average_words: float
    average_images: float
