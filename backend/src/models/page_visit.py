from sqlalchemy import Column, Integer, Text

from src.core.db.database import TimestampMixin, Base


class PageVisit(Base, TimestampMixin):
    __tablename__ = "visits"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(Text, nullable=False, index=True)
    link_count = Column(Integer, nullable=False)
    internal_links = Column(Integer, nullable=True)
    external_links = Column(Integer, nullable=True)
    word_count = Column(Integer, nullable=False)
    image_count = Column(Integer, nullable=False)
    content_images = Column(Integer, nullable=True)
    decorative_images = Column(Integer, nullable=True)
