"""
Test configuration and fixtures for Toán Socratic backend
"""

import os
import pytest
import pytest_asyncio
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock
from uuid import uuid4

from toan_socratic.db.database import get_db
from toan_socratic.db.models import (
    Base,
    DialogueState,
    DifficultyLevel,
    Problem,
    Session,
    SessionStatus,
    User,
)
from toan_socratic.main import app


# Test database URL (use the real async backend instead of aiosqlite, which hangs here)
TEST_DATABASE_URL = os.environ.get(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://toan_user:toan_password@localhost:5433/toansc",
)


@pytest_asyncio.fixture(scope="function", loop_scope="function")
async def schema_name() -> str:
    return f"test_{uuid4().hex}"


@pytest_asyncio.fixture(scope="function", loop_scope="function")
async def session_factory(
    schema_name: str,
) -> AsyncGenerator[async_sessionmaker[AsyncSession], None]:
    """Create a fresh schema-scoped engine/session factory per test loop."""
    admin_engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        future=True,
        poolclass=NullPool,
    )
    async with admin_engine.begin() as conn:
        await conn.exec_driver_sql(f'CREATE SCHEMA IF NOT EXISTS "{schema_name}"')

    test_engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        future=True,
        poolclass=NullPool,
        connect_args={"server_settings": {"search_path": schema_name}},
    )
    factory = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )
    yield factory
    await test_engine.dispose()
    async with admin_engine.begin() as conn:
        await conn.exec_driver_sql(f'DROP SCHEMA IF EXISTS "{schema_name}" CASCADE')
    await admin_engine.dispose()


@pytest_asyncio.fixture(scope="function", loop_scope="function")
async def prepared_db(session_factory: async_sessionmaker[AsyncSession]) -> AsyncGenerator[None, None]:
    """Create and tear down test database tables"""
    test_engine = session_factory.kw["bind"]

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield


@pytest_asyncio.fixture(scope="function", loop_scope="function")
async def db_session(
    prepared_db: None,
    session_factory: async_sessionmaker[AsyncSession],
) -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session"""
    async with session_factory() as session:
        yield session


@pytest_asyncio.fixture(scope="function", loop_scope="function")
async def test_client(
    prepared_db: None,
    session_factory: async_sessionmaker[AsyncSession],
) -> AsyncGenerator[AsyncClient, None]:
    """Create a test HTTP client"""
    async def override_get_db():
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
def mock_llm_client():
    """Mock LLM client for testing"""
    mock_client = AsyncMock()

    # Mock get_response method
    async def mock_get_response(messages, system_prompt, tools=None, max_tokens=1024):
        return "This is a mock AI response for testing purposes."

    # Mock get_response_with_tools method
    async def mock_get_response_with_tools(messages, system_prompt, tools, max_tokens=1024):
        return {
            "text": "Mock response with tools",
            "tool_calls": []
        }

    mock_client.get_response = mock_get_response
    mock_client.get_response_with_tools = mock_get_response_with_tools
    mock_client.provider = "mock"
    mock_client.model = "mock-model"

    return mock_client


@pytest.fixture
def sample_user_data():
    """Sample user data for testing"""
    return {
        "email": "test@example.com",
        "name": "Test User",
        "role": "student"
    }


@pytest.fixture
def sample_problem_data():
    """Sample problem data for testing"""
    return {
        "topic_id": "hinh-hoc.hinh-chop",
        "statement_latex": "Tính thể tích hình chóp S.ABCD có đáy ABCD là hình vuông cạnh $a = 6$ cm.",
        "difficulty": "EASY",
        "answer": "V = 48 cm³",
        "is_geometry": True,
        "geometry_params": {
            "solid_type": "pyramid",
            "params": {
                "base_shape": "square",
                "base_side": 6,
                "height": 4
            }
        },
        "source": "Test Data",
        "misconceptions": ["Test misconception"]
    }


@pytest.fixture
def sample_session_data():
    """Sample session data for testing"""
    return {
        "topic_id": "hinh-hoc.hinh-chop",
        "problem_id": None,
        "status": "active",
        "dialogue_state": "review",
        "hint_level": 0,
        "hint_count": 0,
        "fail_count": 0,
        "messages": []
    }


@pytest_asyncio.fixture(loop_scope="function")
async def sample_user(
    prepared_db: None,
    session_factory: async_sessionmaker[AsyncSession],
    sample_user_data: dict,
) -> User:
    """Create a sample user in database"""
    async with session_factory() as session:
        user = User(
            email=sample_user_data["email"],
            name=sample_user_data["name"],
            role=sample_user_data["role"]
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
    return user


@pytest_asyncio.fixture(loop_scope="function")
async def sample_problem(
    prepared_db: None,
    session_factory: async_sessionmaker[AsyncSession],
    sample_problem_data: dict,
) -> Problem:
    """Create a sample problem in database"""
    async with session_factory() as session:
        problem = Problem(
            topic_id=sample_problem_data["topic_id"],
            statement_latex=sample_problem_data["statement_latex"],
            difficulty=DifficultyLevel[sample_problem_data["difficulty"]],
            answer=sample_problem_data["answer"],
            is_geometry=sample_problem_data["is_geometry"],
            geometry_params=sample_problem_data["geometry_params"],
            source=sample_problem_data["source"],
            misconceptions=sample_problem_data["misconceptions"]
        )
        session.add(problem)
        await session.commit()
        await session.refresh(problem)
    return problem


@pytest_asyncio.fixture(loop_scope="function")
async def sample_session(
    prepared_db: None,
    session_factory: async_sessionmaker[AsyncSession],
    sample_user: User,
    sample_problem: Problem,
) -> Session:
    """Create a sample session in database"""
    async with session_factory() as db:
        session = Session(
            user_id=sample_user.id,
            problem_id=sample_problem.id,
            topic_id="hinh-hoc.hinh-chop",
            status=SessionStatus.ACTIVE,
            dialogue_state=DialogueState.REVIEW,
            hint_level=0,
            hint_count=0,
            fail_count=0,
            messages=[]
        )
        db.add(session)
        await db.commit()
        await db.refresh(session)
        return session


# Pytest configuration
def pytest_configure(config):
    """Configure pytest"""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "api: mark test as an API test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
