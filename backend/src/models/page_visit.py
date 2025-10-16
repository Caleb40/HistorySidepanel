from sqlalchemy import Column, Integer, DateTime, Text

from src.core.db.database import Base
from src.utils.helpers import get_utc_now


class PageVisit(Base):
    __tablename__ = "visits"

    id = Column(Integer, primary_key=True, index=True)
    datetime_visited = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)
    url = Column(Text, nullable=False, index=True)
    link_count = Column(Integer, nullable=False)
    word_count = Column(Integer, nullable=False)
    image_count = Column(Integer, nullable=False)

    def to_dict(self, exclude=None):
        if exclude is None:
            exclude = []
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns.values()
            if column.name not in exclude
        }
