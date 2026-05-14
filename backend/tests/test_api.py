"""
API endpoint tests for Toán Socratic backend
"""

import json
from types import SimpleNamespace
from unittest.mock import AsyncMock
from datetime import datetime, timedelta
from datetime import time as dtime
import pytest
from fastapi import HTTPException
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from uuid import uuid4

from toan_socratic.config import settings
from toan_socratic.db.database import get_db
from toan_socratic.db.models import (
    DialogueState,
    Problem,
    Progress,
    Session,
    SessionStatus,
    User,
    UserRole,
)
from toan_socratic.main import app, create_app


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
    async def test_create_session(
        self,
        test_client: AsyncClient,
        sample_problem: Problem,
        sample_user: User,
        auth_headers: dict[str, str],
    ):
        """Test creating a new session"""
        session_data = {
            "user_id": str(sample_user.id),
            "topic_id": "hinh-hoc.hinh-chop",
            "problem_id": str(sample_problem.id)
        }

        response = await test_client.post(
            "/api/sessions",
            json=session_data,
            headers=auth_headers,
        )
        assert response.status_code == 201

        data = response.json()
        assert "id" in data
        assert data["topic_id"] == "hinh-hoc.hinh-chop"
        assert data["status"] == "active"
        assert data["dialogue_state"] == "review"
        assert data["hint_level"] == 0
        assert data["fail_count"] == 0
        assert data["user_id"] == str(sample_user.id)

    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_create_session_ignores_client_supplied_user_id(
        self,
        test_client: AsyncClient,
        sample_problem: Problem,
        sample_user: User,
        other_user: User,
        auth_headers: dict[str, str],
    ):
        response = await test_client.post(
            "/api/sessions",
            json={
                "user_id": str(other_user.id),
                "topic_id": "hinh-hoc.hinh-chop",
                "problem_id": str(sample_problem.id),
            },
            headers=auth_headers,
        )
        assert response.status_code == 201
        assert response.json()["user_id"] == str(sample_user.id)

    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_get_session(
        self,
        test_client: AsyncClient,
        sample_session: Session,
        auth_headers: dict[str, str],
    ):
        """Test getting session details"""
        response = await test_client.get(
            f"/api/sessions/{sample_session.id}",
            headers=auth_headers,
        )
        assert response.status_code == 200

        data = response.json()
        assert data["id"] == str(sample_session.id)
        assert data["topic_id"] == sample_session.topic_id
        assert data["status"] == sample_session.status.value

    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_get_session_not_found(
        self,
        test_client: AsyncClient,
        auth_headers: dict[str, str],
    ):
        """Test getting non-existent session"""
        fake_id = uuid4()
        response = await test_client.get(f"/api/sessions/{fake_id}", headers=auth_headers)
        assert response.status_code == 404

    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_get_session_forbidden_for_non_owner(
        self,
        test_client: AsyncClient,
        sample_session: Session,
        other_auth_headers: dict[str, str],
    ):
        response = await test_client.get(
            f"/api/sessions/{sample_session.id}",
            headers=other_auth_headers,
        )
        assert response.status_code == 404

    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_send_message(
        self,
        test_client: AsyncClient,
        sample_session: Session,
        mock_llm_client,
        auth_headers: dict[str, str],
    ):
        """Test sending a message to get AI response"""
        message_data = {
            "content": "Tính thể tích hình chóp",
            "hint_requested": False
        }

        # Mock the LLM client using patch
        from unittest.mock import patch
        with patch("toan_socratic.routers.sessions.llm_client", mock_llm_client):
            response = await test_client.post(
                f"/api/sessions/{sample_session.id}/message",
                json=message_data,
                headers=auth_headers,
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
        auth_headers: dict[str, str],
    ):
        from unittest.mock import patch

        await self._persist_session_state(
            session_factory,
            sample_session.id,
            dialogue_state=DialogueState.HEURISTIC,
        )
        llm_client = self._build_prompt_asserting_llm("rectify")

        with patch("toan_socratic.routers.sessions.llm_client", llm_client):
            response = await test_client.post(
                f"/api/sessions/{sample_session.id}/message",
                json={"content": "V = 50 cm3", "hint_requested": False},
                headers=auth_headers,
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
        auth_headers: dict[str, str],
    ):
        from unittest.mock import patch

        await self._persist_session_state(
            session_factory,
            sample_session.id,
            dialogue_state=DialogueState.HEURISTIC,
        )
        llm_client = self._build_prompt_asserting_llm("summarize")

        with patch("toan_socratic.routers.sessions.llm_client", llm_client):
            response = await test_client.post(
                f"/api/sessions/{sample_session.id}/message",
                json={"content": "V = 48 cm3", "hint_requested": False},
                headers=auth_headers,
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
        auth_headers: dict[str, str],
    ):
        from unittest.mock import patch

        await self._persist_session_state(
            session_factory,
            sample_session.id,
            dialogue_state=DialogueState.REVIEW,
        )
        llm_client = self._build_prompt_asserting_llm("heuristic")

        with patch("toan_socratic.routers.sessions.llm_client", llm_client):
            response = await test_client.post(
                f"/api/sessions/{sample_session.id}/message",
                json={"content": "Em biết diện tích đáy là 36 cm2", "hint_requested": False},
                headers=auth_headers,
            )

        assert response.status_code == 200
        data = response.json()
        assert data["message"]["content"] == "response for heuristic"
        assert data["session_state"]["dialogue_state"] == "heuristic"

    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_send_message_stream(
        self,
        test_client: AsyncClient,
        sample_session: Session,
        mock_llm_client,
        auth_headers: dict[str, str],
    ):
        """Test streaming message response shape"""

        async def mock_stream_response(messages, system_prompt, tools=None, max_tokens=1024):
            for chunk in ["Xin chao ", "hoc sinh"]:
                yield chunk

        mock_llm_client.stream_response = mock_stream_response

        from unittest.mock import patch
        with patch("toan_socratic.routers.sessions.llm_client", mock_llm_client):
            response = await test_client.post(
                f"/api/sessions/{sample_session.id}/message?stream=true",
                json={"content": "Bat dau", "hint_requested": False},
                headers=auth_headers,
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
        auth_headers: dict[str, str],
    ):
        from unittest.mock import patch

        await self._persist_session_state(
            session_factory,
            sample_session.id,
            dialogue_state=DialogueState.HEURISTIC,
        )
        llm_client = self._build_prompt_asserting_llm("summarize")

        with patch("toan_socratic.routers.sessions.llm_client", llm_client):
            response = await test_client.post(
                f"/api/sessions/{sample_session.id}/message?stream=true",
                json={"content": "V = 48 cm3", "hint_requested": False},
                headers=auth_headers,
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

        session_response = await test_client.get(
            f"/api/sessions/{sample_session.id}",
            headers=auth_headers,
        )
        assert session_response.status_code == 200
        assert session_response.json()["dialogue_state"] == "summarize"

    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_send_message_stream_error_persists_student_turn(
        self,
        test_client: AsyncClient,
        sample_session: Session,
        mock_llm_client,
        auth_headers: dict[str, str],
    ):
        from unittest.mock import patch

        async def failing_stream_response(messages, system_prompt, tools=None, max_tokens=1024):
            if False:
                yield ""
            raise RuntimeError("llm down")

        mock_llm_client.stream_response = failing_stream_response

        with patch("toan_socratic.routers.sessions.llm_client", mock_llm_client):
            response = await test_client.post(
                f"/api/sessions/{sample_session.id}/message?stream=true",
                json={"content": "Em thu giai bai nay", "hint_requested": False},
                headers=auth_headers,
            )

        assert response.status_code == 200
        events = [
            json.loads(line.removeprefix("data: "))
            for line in response.text.splitlines()
            if line.startswith("data: ")
        ]
        assert events[-1]["error"] == "llm down"

        session_response = await test_client.get(
            f"/api/sessions/{sample_session.id}",
            headers=auth_headers,
        )
        assert session_response.status_code == 200
        data = session_response.json()
        assert data["messages"][-1]["role"] == "user"
        assert data["messages"][-1]["content"] == "Em thu giai bai nay"
        assert data["dialogue_state"] == "heuristic"

    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_send_message_hint_request_transitions_to_rectify(
        self,
        test_client: AsyncClient,
        sample_session: Session,
        mock_llm_client,
        session_factory: async_sessionmaker[AsyncSession],
        auth_headers: dict[str, str],
    ):
        """Test hint requests push the dialogue into rectify mode"""
        from unittest.mock import patch

        await self._persist_session_state(
            session_factory,
            sample_session.id,
            dialogue_state=DialogueState.HEURISTIC,
        )

        with patch("toan_socratic.routers.sessions.llm_client", mock_llm_client):
            response = await test_client.post(
                f"/api/sessions/{sample_session.id}/message",
                json={"content": "Em cần gợi ý", "hint_requested": True},
                headers=auth_headers,
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
        auth_headers: dict[str, str],
    ):
        """Test the first hint request takes precedence over the review state"""
        from unittest.mock import patch

        await self._persist_session_state(
            session_factory,
            sample_session.id,
            dialogue_state=DialogueState.REVIEW,
        )

        with patch("toan_socratic.routers.sessions.llm_client", mock_llm_client):
            response = await test_client.post(
                f"/api/sessions/{sample_session.id}/message",
                json={"content": "", "hint_requested": True},
                headers=auth_headers,
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
        auth_headers: dict[str, str],
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

        with patch("toan_socratic.routers.sessions.llm_client", mock_llm_client):
            response = await test_client.post(
                f"/api/sessions/{sample_session.id}/message",
                json={"content": "Em thử lại", "hint_requested": False},
                headers=auth_headers,
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
        auth_headers: dict[str, str],
    ):
        """Test an incorrect answer-like assertion enters rectify mode"""
        from unittest.mock import patch

        await self._persist_session_state(
            session_factory,
            sample_session.id,
            dialogue_state=DialogueState.HEURISTIC,
        )

        with patch("toan_socratic.routers.sessions.llm_client", mock_llm_client):
            response = await test_client.post(
                f"/api/sessions/{sample_session.id}/message",
                json={"content": "V = 50 cm3", "hint_requested": False},
                headers=auth_headers,
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
        auth_headers: dict[str, str],
    ):
        """Test a correct final answer enters summarize mode"""
        from unittest.mock import patch

        await self._persist_session_state(
            session_factory,
            sample_session.id,
            dialogue_state=DialogueState.HEURISTIC,
        )

        with patch("toan_socratic.routers.sessions.llm_client", mock_llm_client):
            response = await test_client.post(
                f"/api/sessions/{sample_session.id}/message",
                json={"content": "V = 48 cm3", "hint_requested": False},
                headers=auth_headers,
            )

        assert response.status_code == 200
        data = response.json()
        assert data["session_state"]["dialogue_state"] == "summarize"
        assert data["session_state"]["fail_count"] == 0

    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_complete_session(
        self,
        test_client: AsyncClient,
        sample_session: Session,
        auth_headers: dict[str, str],
    ):
        """Test completing a session"""
        completion_data = {
            "student_rating": 5
        }

        response = await test_client.put(
            f"/api/sessions/{sample_session.id}/complete",
            json=completion_data,
            headers=auth_headers,
        )
        assert response.status_code == 200

        data = response.json()
        assert "summary" in data
        assert "mastery_delta" in data
        assert "next_suggested_topic" in data
        assert isinstance(data["mastery_delta"], float)

    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_list_sessions_returns_only_current_user(
        self,
        test_client: AsyncClient,
        sample_session: Session,
        auth_headers: dict[str, str],
    ):
        response = await test_client.get("/api/sessions", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == str(sample_session.id)

    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_list_sessions_omits_messages_but_detail_keeps_them(
        self,
        test_client: AsyncClient,
        sample_session: Session,
        auth_headers: dict[str, str],
        session_factory: async_sessionmaker[AsyncSession],
    ):
        async with session_factory() as db:
            session = await db.get(Session, sample_session.id)
            session.messages = [
                {
                    "role": "user",
                    "content": "Em nghi dap an la 12",
                    "timestamp": datetime.utcnow().isoformat(),
                },
                {
                    "role": "assistant",
                    "content": "Em thu kiem tra lai tung buoc nhe.",
                    "timestamp": datetime.utcnow().isoformat(),
                },
            ]
            await db.commit()

        list_response = await test_client.get("/api/sessions", headers=auth_headers)
        assert list_response.status_code == 200
        list_data = list_response.json()
        assert len(list_data) == 1
        assert "messages" not in list_data[0]

        detail_response = await test_client.get(
            f"/api/sessions/{sample_session.id}",
            headers=auth_headers,
        )
        assert detail_response.status_code == 200
        detail_data = detail_response.json()
        assert len(detail_data["messages"]) == 2
        assert detail_data["messages"][0]["role"] == "user"


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
    async def test_invalid_session_id(
        self,
        test_client: AsyncClient,
        auth_headers: dict[str, str],
    ):
        """Test handling invalid session ID"""
        invalid_id = "not-a-uuid"
        response = await test_client.get(f"/api/sessions/{invalid_id}", headers=auth_headers)
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
    async def test_missing_required_fields(
        self,
        test_client: AsyncClient,
        auth_headers: dict[str, str],
    ):
        """Test handling missing required fields"""
        incomplete_data = {
            "problem_id": str(uuid4())
        }

        response = await test_client.post(
            "/api/sessions",
            json=incomplete_data,
            headers=auth_headers,
        )
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
        client = await self._build_auth_client(
            SimpleNamespace(id=user_id, email="test@example.com", role=UserRole.STUDENT)
        )
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
        client = await self._build_auth_client(
            SimpleNamespace(id=user_id, email="test@example.com", role=UserRole.STUDENT)
        )
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

    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_exchange_google_token(
        self,
        test_client: AsyncClient,
        monkeypatch: pytest.MonkeyPatch,
    ):
        monkeypatch.setattr(settings, "google_client_id", "google-client-id")

        async def fake_verify(_: str) -> dict[str, str]:
            return {
                "sub": "google-sub-123",
                "email": "google@example.com",
                "name": "Google User",
                "picture": "https://example.com/avatar.png",
            }

        monkeypatch.setattr("toan_socratic.routers.auth.verify_google_identity_token", fake_verify)
        response = await test_client.post(
            "/api/auth/google",
            json={"id_token": "signed-google-token"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["token_type"] == "bearer"
        assert data["user"]["email"] == "google@example.com"
        assert data["user"]["role"] == "student"

    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_exchange_google_token_rejects_invalid_token(
        self,
        test_client: AsyncClient,
        monkeypatch: pytest.MonkeyPatch,
    ):
        monkeypatch.setattr(settings, "google_client_id", "google-client-id")

        async def fake_verify(_: str) -> dict[str, str]:
            raise HTTPException(status_code=401, detail="Invalid Google ID token")

        monkeypatch.setattr("toan_socratic.routers.auth.verify_google_identity_token", fake_verify)
        response = await test_client.post(
            "/api/auth/google",
            json={"id_token": "bad-token"},
        )
        assert response.status_code == 401

    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_exchange_google_token_does_not_auto_link_admin_by_email(
        self,
        test_client: AsyncClient,
        admin_user: User,
        monkeypatch: pytest.MonkeyPatch,
        session_factory: async_sessionmaker[AsyncSession],
    ):
        monkeypatch.setattr(settings, "google_client_id", "google-client-id")

        async def fake_verify(_: str) -> dict[str, str]:
            return {
                "sub": "attacker-google-sub",
                "email": admin_user.email,
                "name": "Admin User",
                "picture": "",
            }

        monkeypatch.setattr("toan_socratic.routers.auth.verify_google_identity_token", fake_verify)
        response = await test_client.post(
            "/api/auth/google",
            json={"id_token": "signed-google-token"},
        )
        assert response.status_code == 409

        async with session_factory() as db:
            user = await db.get(User, admin_user.id)
            assert user.auth_provider is None
            assert user.auth_subject is None


class TestProgressAndAdminEndpoints:
    async def _create_completed_session(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        *,
        user_id,
        topic_id: str,
        started_at: datetime,
        ended_at: datetime | None = None,
    ) -> Session:
        async with session_factory() as db:
            session = Session(
                user_id=user_id,
                topic_id=topic_id,
                status=SessionStatus.COMPLETED,
                dialogue_state=DialogueState.SUMMARIZE,
                hint_level=0,
                hint_count=0,
                fail_count=0,
                messages=[],
                summary="Hoan thanh",
                started_at=started_at,
                ended_at=ended_at,
            )
            db.add(session)
            await db.commit()
            await db.refresh(session)
            return session

    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_complete_session_creates_progress(
        self,
        test_client: AsyncClient,
        sample_session: Session,
        sample_user: User,
        auth_headers: dict[str, str],
        session_factory: async_sessionmaker[AsyncSession],
    ):
        response = await test_client.put(
            f"/api/sessions/{sample_session.id}/complete",
            json={"student_rating": 5},
            headers=auth_headers,
        )
        assert response.status_code == 200

        async with session_factory() as db:
            progress = await db.get(
                Progress,
                {"user_id": sample_user.id, "topic_id": sample_session.topic_id},
            )
            assert progress is not None
            assert progress.sessions_count == 1
            assert progress.mastery_score > 0

    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_complete_session_is_idempotent_for_progress(
        self,
        test_client: AsyncClient,
        sample_session: Session,
        sample_user: User,
        auth_headers: dict[str, str],
        session_factory: async_sessionmaker[AsyncSession],
    ):
        first_response = await test_client.put(
            f"/api/sessions/{sample_session.id}/complete",
            json={"student_rating": 5},
            headers=auth_headers,
        )
        assert first_response.status_code == 200

        second_response = await test_client.put(
            f"/api/sessions/{sample_session.id}/complete",
            json={"student_rating": 1},
            headers=auth_headers,
        )
        assert second_response.status_code == 200

        async with session_factory() as db:
            session = await db.get(Session, sample_session.id)
            progress = await db.get(
                Progress,
                {"user_id": sample_user.id, "topic_id": sample_session.topic_id},
            )
            assert session.student_rating == 5
            assert progress.sessions_count == 1
            assert progress.mastery_score == first_response.json()["mastery_delta"]

    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_get_progress_me(
        self,
        test_client: AsyncClient,
        sample_session: Session,
        auth_headers: dict[str, str],
    ):
        complete_response = await test_client.put(
            f"/api/sessions/{sample_session.id}/complete",
            json={"student_rating": 4},
            headers=auth_headers,
        )
        assert complete_response.status_code == 200

        response = await test_client.get("/api/progress/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert sample_session.topic_id in data["mastery_by_topic"]
        assert data["sessions_this_week"] >= 1
        assert isinstance(data["weekly_activity"], list)

    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_progress_counts_all_recent_sessions_when_more_than_thirty(
        self,
        test_client: AsyncClient,
        sample_user: User,
        auth_headers: dict[str, str],
        session_factory: async_sessionmaker[AsyncSession],
    ):
        today = datetime.utcnow().date()
        for offset in range(35):
            day_offset = offset % 7
            started_at = datetime.combine(
                today - timedelta(days=day_offset),
                dtime(hour=12, minute=offset % 60),
            )
            await self._create_completed_session(
                session_factory,
                user_id=sample_user.id,
                topic_id="hinh-hoc.hinh-chop",
                started_at=started_at,
                ended_at=started_at + timedelta(minutes=20),
            )

        response = await test_client.get("/api/progress/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()

        assert data["sessions_this_week"] == 35
        assert sum(day["sessions"] for day in data["weekly_activity"]) == 35

    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_progress_streak_uses_full_recent_dataset(
        self,
        test_client: AsyncClient,
        sample_user: User,
        auth_headers: dict[str, str],
        session_factory: async_sessionmaker[AsyncSession],
    ):
        today = datetime.utcnow().date()
        for offset in range(31):
            day_offset = offset % 6
            started_at = datetime.combine(
                today - timedelta(days=day_offset),
                dtime(hour=12, minute=offset % 60),
            )
            await self._create_completed_session(
                session_factory,
                user_id=sample_user.id,
                topic_id="hinh-hoc.hinh-chop",
                started_at=started_at,
                ended_at=started_at + timedelta(minutes=15),
            )
        started_at = datetime.combine(today - timedelta(days=6), dtime(hour=9, minute=0))
        await self._create_completed_session(
            session_factory,
            user_id=sample_user.id,
            topic_id="hinh-hoc.hinh-chop",
            started_at=started_at,
            ended_at=started_at + timedelta(minutes=15),
        )

        response = await test_client.get("/api/progress/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()

        assert data["streak_days"] == 7

    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_progress_weekly_activity_matches_recent_completion_total(
        self,
        test_client: AsyncClient,
        sample_user: User,
        auth_headers: dict[str, str],
        session_factory: async_sessionmaker[AsyncSession],
    ):
        today = datetime.utcnow().date()
        total_recent_sessions = 0

        for day_offset in range(7):
            sessions_for_day = day_offset + 1
            total_recent_sessions += sessions_for_day
            for session_index in range(sessions_for_day):
                started_at = datetime.combine(
                    today - timedelta(days=day_offset),
                    dtime(hour=12, minute=session_index),
                )
                await self._create_completed_session(
                    session_factory,
                    user_id=sample_user.id,
                    topic_id="giai-tich.dao-ham",
                    started_at=started_at,
                    ended_at=started_at + timedelta(minutes=10),
                )

        response = await test_client.get("/api/progress/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()

        assert sum(day["sessions"] for day in data["weekly_activity"]) == total_recent_sessions

    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_progress_excludes_future_dated_completions(
        self,
        test_client: AsyncClient,
        sample_user: User,
        auth_headers: dict[str, str],
        session_factory: async_sessionmaker[AsyncSession],
    ):
        now = datetime.utcnow().replace(microsecond=0)
        completed_recently = now - timedelta(minutes=5)
        future_completion = now + timedelta(days=1)

        await self._create_completed_session(
            session_factory,
            user_id=sample_user.id,
            topic_id="giai-tich.dao-ham",
            started_at=completed_recently - timedelta(minutes=20),
            ended_at=completed_recently,
        )
        await self._create_completed_session(
            session_factory,
            user_id=sample_user.id,
            topic_id="giai-tich.dao-ham",
            started_at=completed_recently,
            ended_at=future_completion,
        )

        response = await test_client.get("/api/progress/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()

        assert data["sessions_this_week"] == 1
        assert sum(day["sessions"] for day in data["weekly_activity"]) == 1

    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_admin_stats_forbidden_for_student(
        self,
        test_client: AsyncClient,
        auth_headers: dict[str, str],
    ):
        response = await test_client.get("/api/admin/stats", headers=auth_headers)
        assert response.status_code == 403

    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_admin_stats_for_admin(
        self,
        test_client: AsyncClient,
        sample_session: Session,
        admin_auth_headers: dict[str, str],
        auth_headers: dict[str, str],
    ):
        await test_client.put(
            f"/api/sessions/{sample_session.id}/complete",
            json={"student_rating": 4},
            headers=auth_headers,
        )

        response = await test_client.get("/api/admin/stats", headers=admin_auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total_users"] >= 2
        assert data["completed_sessions"] >= 1

    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_admin_stats_active_students_excludes_admin_sessions(
        self,
        test_client: AsyncClient,
        sample_user: User,
        admin_user: User,
        admin_auth_headers: dict[str, str],
        session_factory: async_sessionmaker[AsyncSession],
    ):
        now = datetime.utcnow().replace(microsecond=0)
        await self._create_completed_session(
            session_factory,
            user_id=sample_user.id,
            topic_id="hinh-hoc.hinh-chop",
            started_at=now - timedelta(days=1),
            ended_at=now - timedelta(days=1) + timedelta(minutes=30),
        )
        await self._create_completed_session(
            session_factory,
            user_id=admin_user.id,
            topic_id="hinh-hoc.hinh-chop",
            started_at=now - timedelta(days=1, hours=1),
            ended_at=now - timedelta(days=1, hours=1) + timedelta(minutes=30),
        )

        response = await test_client.get("/api/admin/stats", headers=admin_auth_headers)
        assert response.status_code == 200
        data = response.json()

        assert data["active_students"] == 1


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
