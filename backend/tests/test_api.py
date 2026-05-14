"""
API endpoint tests for Toán Socratic backend
"""

import json
from types import SimpleNamespace
from unittest.mock import AsyncMock
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from uuid import uuid4

from config import settings
from db.database import get_db
from db.models import User, Session, Problem, DialogueState
from main import app, create_app


class TestHealthEndpoints:
    """Test health check endpoints"""

    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_root_endpoint(self, test_client: AsyncClient):
        """Test root endpoint returns health status"""
        response = await test_client.get("/")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "Toán Socratic API"
        assert "version" in data

    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_health_endpoint(self, test_client: AsyncClient):
        """Test health endpoint"""
        response = await test_client.get("/health")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "ok"


class TestSessionsEndpoints:
    """Test sessions API endpoints"""

    @staticmethod
    def _build_prompt_asserting_llm(expected_state: str) -> SimpleNamespace:
        async def mock_get_response(messages, system_prompt, tools=None, max_tokens=1024):
            assert f"Hiện tại: {expected_state}" in system_prompt
            return f"response for {expected_state}"

        async def mock_stream_response(messages, system_prompt, tools=None, max_tokens=1024):
            assert f"Hiện tại: {expected_state}" in system_prompt
            for chunk in ["stream ", expected_state]:
                yield chunk

        return SimpleNamespace(
            get_response=mock_get_response,
            get_response_with_tools=AsyncMock(
                return_value={"text": f"response for {expected_state}", "tool_calls": []}
            ),
            stream_response=mock_stream_response,
            provider="mock",
            model="mock-model",
        )

    @staticmethod
    async def _persist_session_state(
        session_factory: async_sessionmaker[AsyncSession],
        session_id,
        *,
        dialogue_state: DialogueState | None = None,
        hint_level: int | None = None,
        fail_count: int | None = None,
    ) -> None:
        async with session_factory() as db:
            session = await db.get(Session, session_id)
            if dialogue_state is not None:
                session.dialogue_state = dialogue_state
            if hint_level is not None:
                session.hint_level = hint_level
            if fail_count is not None:
                session.fail_count = fail_count
            await db.commit()

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
            assert data["session_state"]["dialogue_state"] == "heuristic"

    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_send_message_uses_rectify_prompt_on_incorrect_turn(
        self,
        test_client: AsyncClient,
        sample_session: Session,
        session_factory: async_sessionmaker[AsyncSession],
    ):
        from unittest.mock import patch

        await self._persist_session_state(
            session_factory,
            sample_session.id,
            dialogue_state=DialogueState.HEURISTIC,
        )
        llm_client = self._build_prompt_asserting_llm("rectify")

        with patch("routers.sessions.llm_client", llm_client):
            response = await test_client.post(
                f"/api/sessions/{sample_session.id}/message",
                json={"content": "V = 50 cm3", "hint_requested": False},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["message"]["content"] == "response for rectify"
        assert data["session_state"]["dialogue_state"] == "rectify"

    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_send_message_uses_summarize_prompt_on_correct_turn(
        self,
        test_client: AsyncClient,
        sample_session: Session,
        session_factory: async_sessionmaker[AsyncSession],
    ):
        from unittest.mock import patch

        await self._persist_session_state(
            session_factory,
            sample_session.id,
            dialogue_state=DialogueState.HEURISTIC,
        )
        llm_client = self._build_prompt_asserting_llm("summarize")

        with patch("routers.sessions.llm_client", llm_client):
            response = await test_client.post(
                f"/api/sessions/{sample_session.id}/message",
                json={"content": "V = 48 cm3", "hint_requested": False},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["message"]["content"] == "response for summarize"
        assert data["session_state"]["dialogue_state"] == "summarize"

    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_send_message_uses_heuristic_prompt_on_progressing_turn(
        self,
        test_client: AsyncClient,
        sample_session: Session,
        session_factory: async_sessionmaker[AsyncSession],
    ):
        from unittest.mock import patch

        await self._persist_session_state(
            session_factory,
            sample_session.id,
            dialogue_state=DialogueState.REVIEW,
        )
        llm_client = self._build_prompt_asserting_llm("heuristic")

        with patch("routers.sessions.llm_client", llm_client):
            response = await test_client.post(
                f"/api/sessions/{sample_session.id}/message",
                json={"content": "Em biết diện tích đáy là 36 cm2", "hint_requested": False},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["message"]["content"] == "response for heuristic"
        assert data["session_state"]["dialogue_state"] == "heuristic"

    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_send_message_stream(self, test_client: AsyncClient, sample_session: Session, mock_llm_client):
        """Test streaming message response shape"""

        async def mock_stream_response(messages, system_prompt, tools=None, max_tokens=1024):
            for chunk in ["Xin chao ", "hoc sinh"]:
                yield chunk

        mock_llm_client.stream_response = mock_stream_response

        from unittest.mock import patch
        with patch('routers.sessions.llm_client', mock_llm_client):
            response = await test_client.post(
                f"/api/sessions/{sample_session.id}/message?stream=true",
                json={"content": "Bat dau", "hint_requested": False},
            )

        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/event-stream")

        events = [
            json.loads(line.removeprefix("data: "))
            for line in response.text.splitlines()
            if line.startswith("data: ")
        ]
        assert events[0] == {"content": "Xin chao ", "done": False}
        assert events[1] == {"content": "hoc sinh", "done": False}
        assert events[-1]["done"] is True
        assert events[-1]["session_state"]["dialogue_state"] == "heuristic"

    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_send_message_stream_uses_current_turn_state_and_commits(
        self,
        test_client: AsyncClient,
        sample_session: Session,
        session_factory: async_sessionmaker[AsyncSession],
    ):
        from unittest.mock import patch

        await self._persist_session_state(
            session_factory,
            sample_session.id,
            dialogue_state=DialogueState.HEURISTIC,
        )
        llm_client = self._build_prompt_asserting_llm("summarize")

        with patch("routers.sessions.llm_client", llm_client):
            response = await test_client.post(
                f"/api/sessions/{sample_session.id}/message?stream=true",
                json={"content": "V = 48 cm3", "hint_requested": False},
            )

        assert response.status_code == 200

        events = [
            json.loads(line.removeprefix("data: "))
            for line in response.text.splitlines()
            if line.startswith("data: ")
        ]
        assert all("error" not in event for event in events)
        assert events[-1]["done"] is True
        assert events[-1]["session_state"]["dialogue_state"] == "summarize"

        session_response = await test_client.get(f"/api/sessions/{sample_session.id}")
        assert session_response.status_code == 200
        assert session_response.json()["dialogue_state"] == "summarize"

    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_send_message_hint_request_transitions_to_rectify(
        self,
        test_client: AsyncClient,
        sample_session: Session,
        mock_llm_client,
        session_factory: async_sessionmaker[AsyncSession],
    ):
        """Test hint requests push the dialogue into rectify mode"""
        from unittest.mock import patch

        await self._persist_session_state(
            session_factory,
            sample_session.id,
            dialogue_state=DialogueState.HEURISTIC,
        )

        with patch('routers.sessions.llm_client', mock_llm_client):
            response = await test_client.post(
                f"/api/sessions/{sample_session.id}/message",
                json={"content": "Em cần gợi ý", "hint_requested": True},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["session_state"]["dialogue_state"] == "rectify"
        assert data["session_state"]["hint_level"] == 1

    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_send_message_first_hint_from_review_transitions_to_rectify(
        self,
        test_client: AsyncClient,
        sample_session: Session,
        mock_llm_client,
        session_factory: async_sessionmaker[AsyncSession],
    ):
        """Test the first hint request takes precedence over the review state"""
        from unittest.mock import patch

        await self._persist_session_state(
            session_factory,
            sample_session.id,
            dialogue_state=DialogueState.REVIEW,
        )

        with patch('routers.sessions.llm_client', mock_llm_client):
            response = await test_client.post(
                f"/api/sessions/{sample_session.id}/message",
                json={"content": "", "hint_requested": True},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["session_state"]["dialogue_state"] == "rectify"
        assert data["session_state"]["hint_level"] == 1

    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_send_message_rectify_persists_after_non_hint_follow_up(
        self,
        test_client: AsyncClient,
        sample_session: Session,
        mock_llm_client,
        session_factory: async_sessionmaker[AsyncSession],
    ):
        """Test a substantive follow-up can recover rectify back to heuristic"""
        from unittest.mock import patch

        await self._persist_session_state(
            session_factory,
            sample_session.id,
            dialogue_state=DialogueState.RECTIFY,
            hint_level=1,
            fail_count=1,
        )

        with patch('routers.sessions.llm_client', mock_llm_client):
            response = await test_client.post(
                f"/api/sessions/{sample_session.id}/message",
                json={"content": "Em thử lại", "hint_requested": False},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["session_state"]["dialogue_state"] == "heuristic"
        assert data["session_state"]["fail_count"] == 0
        assert data["session_state"]["hint_level"] == 1

    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_send_message_incorrect_assertion_transitions_to_rectify(
        self,
        test_client: AsyncClient,
        sample_session: Session,
        mock_llm_client,
        session_factory: async_sessionmaker[AsyncSession],
    ):
        """Test an incorrect answer-like assertion enters rectify mode"""
        from unittest.mock import patch

        await self._persist_session_state(
            session_factory,
            sample_session.id,
            dialogue_state=DialogueState.HEURISTIC,
        )

        with patch('routers.sessions.llm_client', mock_llm_client):
            response = await test_client.post(
                f"/api/sessions/{sample_session.id}/message",
                json={"content": "V = 50 cm3", "hint_requested": False},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["session_state"]["dialogue_state"] == "rectify"
        assert data["session_state"]["fail_count"] >= 1

    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_send_message_matching_answer_transitions_to_summarize(
        self,
        test_client: AsyncClient,
        sample_session: Session,
        mock_llm_client,
        session_factory: async_sessionmaker[AsyncSession],
    ):
        """Test a correct final answer enters summarize mode"""
        from unittest.mock import patch

        await self._persist_session_state(
            session_factory,
            sample_session.id,
            dialogue_state=DialogueState.HEURISTIC,
        )

        with patch('routers.sessions.llm_client', mock_llm_client):
            response = await test_client.post(
                f"/api/sessions/{sample_session.id}/message",
                json={"content": "V = 48 cm3", "hint_requested": False},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["session_state"]["dialogue_state"] == "summarize"
        assert data["session_state"]["fail_count"] == 0

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


class TestAuthEndpoints:
    """Test auth API endpoints"""

    async def _build_auth_client(self, mocked_user):
        db_session = AsyncMock()
        execute_result = SimpleNamespace(
            scalars=lambda: SimpleNamespace(first=lambda: mocked_user)
        )
        db_session.execute.return_value = execute_result

        async def override_get_db():
            yield db_session

        app.dependency_overrides[get_db] = override_get_db
        client = AsyncClient(transport=ASGITransport(app=app), base_url="http://test")
        return client

    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_generate_token_requires_bridge_header(self):
        user_id = uuid4()
        client = await self._build_auth_client(SimpleNamespace(id=user_id, email="test@example.com"))
        try:
            response = await client.post("/api/auth/token", json={"user_id": str(user_id)})
        finally:
            await client.aclose()
            app.dependency_overrides.clear()
        assert response.status_code == 401

    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_generate_token(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setattr(settings, "auth_bridge_secret", "test-bridge-secret")
        user_id = uuid4()
        client = await self._build_auth_client(SimpleNamespace(id=user_id, email="test@example.com"))
        try:
            response = await client.post(
                "/api/auth/token",
                json={"user_id": str(user_id)},
                headers={"X-Auth-Bridge-Secret": "test-bridge-secret"},
            )
        finally:
            await client.aclose()
            app.dependency_overrides.clear()
        assert response.status_code == 200

        data = response.json()
        assert data["token_type"] == "bearer"
        assert isinstance(data["access_token"], str)
        assert data["access_token"]

    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_generate_token_user_not_found(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setattr(settings, "auth_bridge_secret", "test-bridge-secret")
        client = await self._build_auth_client(None)
        try:
            response = await client.post(
                "/api/auth/token",
                json={"user_id": str(uuid4())},
                headers={"X-Auth-Bridge-Secret": "test-bridge-secret"},
            )
        finally:
            await client.aclose()
            app.dependency_overrides.clear()
        assert response.status_code == 404


class TestCorsConfiguration:
    """Test CORS configuration"""

    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_cors_allows_configured_origin(self):
        app = create_app(cors_origins=["http://localhost:3000", "http://127.0.0.1:3000"])

        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            response = await client.options(
                "/health",
                headers={
                    "Origin": "http://127.0.0.1:3000",
                    "Access-Control-Request-Method": "GET",
                },
            )

        assert response.status_code == 200
        assert response.headers["access-control-allow-origin"] == "http://127.0.0.1:3000"
