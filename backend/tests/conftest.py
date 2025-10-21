import asyncio
import os
import sys

import pytest
from dotenv import load_dotenv
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from starlette.testclient import TestClient

load_dotenv()

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.db.database import Base
from src.api.v1.routes.page_visits import router
from src.core.db.database import async_get_db

POSTGRES_USER = os.getenv("POSTGRES_USER", "TestUser")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "your_password_here")
POSTGRES_SERVER = os.getenv("POSTGRES_SERVER", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5433")
POSTGRES_DB = os.getenv("POSTGRES_DB", "host.docker.internal")

TEST_DATABASE_URL = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
async def setup_test_database():
    """Just manage tables, not the whole database"""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False, future=True)

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield

    # Drop tables (clean up)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture(scope="function")
async def engine_test():
    """Engine for the test database"""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False, future=True)
    yield engine
    await engine.dispose()


@pytest.fixture(scope="function")
async def setup_database(engine_test):
    """Clear and recreate tables for each test function"""
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield


@pytest.fixture(scope="function")
async def db_session(engine_test):
    """Database session for service layer tests"""
    AsyncSessionLocal = sessionmaker(engine_test, class_=AsyncSession, expire_on_commit=False)
    async with AsyncSessionLocal() as session:
        yield session


async def override_get_db():
    """Override FastAPI dependency for DB"""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False, future=True)
    AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with AsyncSessionLocal() as session:
        yield session


@pytest.fixture()
async def test_app():
    """FastAPI app fixture for endpoint tests"""
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[async_get_db] = override_get_db
    return app


@pytest.fixture()
def client(test_app):
    """Test client fixture for making requests"""
    with TestClient(test_app) as client:
        yield client
