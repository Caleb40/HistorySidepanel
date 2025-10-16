from datetime import datetime, timezone
from typing import Any, AsyncGenerator

from sqlalchemy import DateTime
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.orm import sessionmaker

from src.core.config import settings


class Base(DeclarativeBase):
    """Base model with created_at and updated_at timestamps"""

    def to_dict(self, exclude=None):
        """
        Convert the model instance to a dictionary.

        Args:
            exclude (list): List of fields to exclude.

        Returns:
            dict: Dictionary representation of the model.
        """
        if exclude is None:
            exclude = []

        # Convert columns collection to a list and filter out the excluded fields
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns.values()
            if column.name not in exclude
        }


class TimestampMixin:
    """Mixin to add created_at and updated_at timestamps to models"""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )


DATABASE_URI = settings.POSTGRES_URI
DATABASE_PREFIX = settings.POSTGRES_ASYNC_PREFIX
DATABASE_URL = f"{DATABASE_PREFIX}{DATABASE_URI}"

async_engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # Log all SQL queries to std. out (default=False)
    future=True,
    pool_size=10,  # active connections
    max_overflow=20,  # extra connections beyond pool_size
    pool_timeout=60,
)

local_session = sessionmaker(
    bind=async_engine, class_=AsyncSession, expire_on_commit=False
)


async def async_get_db() -> AsyncGenerator[Any, Any]:
    async_session = local_session
    async with async_session() as db:
        yield db
