"""
API endpoint tests for Toán Socratic backend
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import uuid4

from db.models import User, Session, Problem, DifficultyLevel, DialogueState, SessionStatus


class TestHealthEndpoints:
    """Test health check endpoints"""

    @pytest.mark.api
    async def test_root_endpoint(self, test_client: AsyncClient):
        """Test root endpoint returns health status"""
        response = await test_client.get("/")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "Toán Socratic API"
        assert "version" in data

    @pytest.mark.api
    async def test_health_endpoint(self, test_client: AsyncClient):
        """Test health endpoint"""
        response = await test_client.get("/health")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "ok"


class TestSessionsEndpoints:
    """Test sessions API endpoints"""

    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_create_session(self, test_client: AsyncClient, sample_problem: Problem, sample_user: User):
        """Test creating a new session"""
        session_data = {
            "user_id": str(sample_user.id),
            "topic_id": "hinh-hoc.hinh-chop",
            "problem_id": str(sample_problem.id)
        }

        response = await test_client.post("/api/sessions", json=session_data)
        assert response.status_code == 201

        data = response.json()
        assert "id" in data
        assert data["topic_id"] == "hinh-hoc.hinh-chop"
        assert data["status"] == "active"
        assert data["dialogue_state"] == "review"
        assert data["hint_level"] == 0
        assert data["fail_count"] == 0

    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_get_session(self, test_client: AsyncClient, sample_session: Session):
        """Test getting session details"""
        response = await test_client.get(f"/api/sessions/{sample_session.id}")
        assert response.status_code == 200

        data = response.json()
        assert data["id"] == str(sample_session.id)
        assert data["topic_id"] == sample_session.topic_id
        assert data["status"] == sample_session.status.value

    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_get_session_not_found(self, test_client: AsyncClient):
        """Test getting non-existent session"""
        fake_id = uuid4()
        response = await test_client.get(f"/api/sessions/{fake_id}")
        assert response.status_code == 404

    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_send_message(self, test_client: AsyncClient, sample_session: Session, mock_llm_client):
        """Test sending a message to get AI response"""
        message_data = {
            "content": "Tính thể tích hình chóp",
            "hint_requested": False
        }

        # Mock the LLM client using patch
        from unittest.mock import patch
        with patch('routers.sessions.llm_client', mock_llm_client):
            response = await test_client.post(
                f"/api/sessions/{sample_session.id}/message",
                json=message_data
            )
            if response.status_code != 200:
                print(f"Error response: {response.text}")
            assert response.status_code == 200

            data = response.json()
            assert "message" in data
            assert "session_state" in data
            assert data["message"]["role"] == "assistant"
            assert data["message"]["content"] is not None

    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_complete_session(self, test_client: AsyncClient, sample_session: Session):
        """Test completing a session"""
        completion_data = {
            "student_rating": 5
        }

        response = await test_client.put(
            f"/api/sessions/{sample_session.id}/complete",
            json=completion_data
        )
        assert response.status_code == 200

        data = response.json()
        assert "summary" in data
        assert "mastery_delta" in data
        assert "next_suggested_topic" in data
        assert isinstance(data["mastery_delta"], float)


class TestProblemsEndpoints:
    """Test problems API endpoints"""

    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_list_problems(self, test_client: AsyncClient, sample_problem: Problem):
        """Test listing problems"""
        response = await test_client.get("/api/problems")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_list_problems_with_filters(self, test_client: AsyncClient, sample_problem: Problem):
        """Test listing problems with filters"""
        response = await test_client.get(
            "/api/problems",
            params={"topic_id": "hinh-hoc.hinh-chop", "difficulty": "easy"}
        )
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)

    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_get_problem(self, test_client: AsyncClient, sample_problem: Problem):
        """Test getting problem details"""
        response = await test_client.get(f"/api/problems/{sample_problem.id}")
        assert response.status_code == 200

        data = response.json()
        assert data["id"] == str(sample_problem.id)
        assert data["topic_id"] == sample_problem.topic_id
        assert data["difficulty"] == sample_problem.difficulty.value

    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_get_problem_not_found(self, test_client: AsyncClient):
        """Test getting non-existent problem"""
        fake_id = uuid4()
        response = await test_client.get(f"/api/problems/{fake_id}")
        assert response.status_code == 404

    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_get_geometry_params(self, test_client: AsyncClient, sample_problem: Problem):
        """Test getting geometry parameters"""
        response = await test_client.get(f"/api/problems/{sample_problem.id}/geometry")
        assert response.status_code == 200

        data = response.json()
        assert "solid_type" in data
        assert data["solid_type"] == "pyramid"

    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_create_problem(self, test_client: AsyncClient):
        """Test creating a new problem"""
        problem_data = {
            "topic_id": "giai-tich.dao-ham",
            "statement_latex": "Tính đạo hàm của hàm số $f(x) = x^3 - 2x^2 + 3x - 1$.",
            "difficulty": "easy",
            "answer": "f'(x) = 3x² - 4x + 3",
            "is_geometry": False,
            "geometry_params": None,
            "source": "Test",
            "misconceptions": ["Test misconception"]
        }

        response = await test_client.post("/api/problems", json=problem_data)
        assert response.status_code == 201

        data = response.json()
        assert "id" in data
        assert data["topic_id"] == "giai-tich.dao-ham"
        assert data["difficulty"] == "easy"


class TestErrorHandling:
    """Test error handling"""

    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_invalid_session_id(self, test_client: AsyncClient):
        """Test handling invalid session ID"""
        invalid_id = "not-a-uuid"
        response = await test_client.get(f"/api/sessions/{invalid_id}")
        assert response.status_code == 422  # Validation error

    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_invalid_problem_data(self, test_client: AsyncClient):
        """Test handling invalid problem data"""
        invalid_data = {
            "topic_id": "",  # Empty topic_id
            "statement_latex": "Test problem",
            "difficulty": "INVALID",  # Invalid difficulty
            "answer": "42"
        }

        response = await test_client.post("/api/problems", json=invalid_data)
        assert response.status_code == 422  # Validation error

    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_missing_required_fields(self, test_client: AsyncClient):
        """Test handling missing required fields"""
        incomplete_data = {
            "topic_id": "test-topic"
            # Missing required user_id field
        }

        response = await test_client.post("/api/sessions", json=incomplete_data)
        assert response.status_code == 422  # Validation error