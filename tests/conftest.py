"""Pytest configuration and fixtures."""

import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from src.config import settings
from src.database import Base, get_database
from src.main import app


@pytest.fixture
async def test_db():
    """Create a test database and yield a session."""
    # Create test database engine
    test_engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
        future=True,
    )

    # Create tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Create session factory
    TestSessionLocal = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async def override_get_database():
        async with TestSessionLocal() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    app.dependency_overrides[get_database] = override_get_database

    yield TestSessionLocal

    # Cleanup
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await test_engine.dispose()
    app.dependency_overrides.clear()


@pytest.fixture
def client():
    """Create a test client."""
    from fastapi.testclient import TestClient

    return TestClient(app)
