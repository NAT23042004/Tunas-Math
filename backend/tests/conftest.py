"""
Test configuration and fixtures for Toán Socratic backend
"""

import pytest
import asyncio
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, MagicMock

from main import app
from db.models import Base, User, Problem, Session, Progress, DifficultyLevel, DialogueState, SessionStatus
from db.database import get_db
from ai.llm_client import llm_client


# Test database URL (using SQLite for tests)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


# Create test engine
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    future=True
)

TestSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)


@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session"""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestSessionLocal() as session:
        yield session

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
async def test_client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create a test HTTP client"""
    async def override_get_db():
        yield db_session

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


@pytest.fixture
async def sample_user(db_session: AsyncSession, sample_user_data: dict) -> User:
    """Create a sample user in database"""
    user = User(
        email=sample_user_data["email"],
        name=sample_user_data["name"],
        role=sample_user_data["role"]
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def sample_problem(db_session: AsyncSession, sample_problem_data: dict) -> Problem:
    """Create a sample problem in database"""
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
    db_session.add(problem)
    await db_session.commit()
    await db_session.refresh(problem)
    return problem


@pytest.fixture
async def sample_session(db_session: AsyncSession, sample_user: User, sample_problem: Problem) -> Session:
    """Create a sample session in database"""
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
    db_session.add(session)
    await db_session.commit()
    await db_session.refresh(session)
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