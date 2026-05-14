"""
Database model tests for Toán Socratic backend
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select
from sqlalchemy.orm import selectinload
from datetime import datetime, timezone
from uuid import uuid4

from toan_socratic.db.models import (
    User, Problem, Session, Progress,
    UserRole, SessionStatus, DialogueState, DifficultyLevel
)


class TestUserModel:
    """Test User model"""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_create_user(self, db_session: AsyncSession):
        """Test creating a user"""
        user = User(
            email="test@example.com",
            name="Test User",
            role=UserRole.STUDENT
        )

        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.name == "Test User"
        assert user.role == UserRole.STUDENT
        assert user.created_at is not None

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_user_unique_email(self, db_session: AsyncSession):
        """Test user email uniqueness constraint"""
        user1 = User(email="test@example.com", name="User 1", role=UserRole.STUDENT)
        user2 = User(email="test@example.com", name="User 2", role=UserRole.STUDENT)

        db_session.add(user1)
        await db_session.commit()

        db_session.add(user2)
        with pytest.raises(Exception):  # Should raise integrity error
            await db_session.commit()

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_user_relationships(self, db_session: AsyncSession):
        """Test user relationships"""
        user = User(email="test@example.com", name="Test User", role=UserRole.STUDENT)
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        # Create session for user
        session = Session(
            user_id=user.id,
            topic_id="test-topic",
            status=SessionStatus.ACTIVE,
            dialogue_state=DialogueState.REVIEW,
            hint_level=0,
            hint_count=0,
            fail_count=0,
            messages=[]
        )
        db_session.add(session)
        await db_session.commit()

        # Refresh user with relationships loaded
        result = await db_session.execute(
            select(User).options(selectinload(User.sessions)).where(User.id == user.id)
        )
        user = result.scalar_one()

        assert len(user.sessions) == 1
        assert user.sessions[0].topic_id == "test-topic"


class TestProblemModel:
    """Test Problem model"""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_create_problem(self, db_session: AsyncSession):
        """Test creating a problem"""
        problem = Problem(
            topic_id="hinh-hoc.hinh-chop",
            statement_latex="Tính thể tích hình chóp",
            difficulty=DifficultyLevel.EASY,
            answer="V = 48 cm³",
            is_geometry=True,
            geometry_params={"solid_type": "pyramid"},
            source="Test",
            misconceptions=["Test misconception"]
        )

        db_session.add(problem)
        await db_session.commit()
        await db_session.refresh(problem)

        assert problem.id is not None
        assert problem.topic_id == "hinh-hoc.hinh-chop"
        assert problem.difficulty == DifficultyLevel.EASY
        assert problem.is_geometry is True
        assert problem.geometry_params["solid_type"] == "pyramid"

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_problem_without_geometry(self, db_session: AsyncSession):
        """Test creating a non-geometry problem"""
        problem = Problem(
            topic_id="giai-tich.dao-ham",
            statement_latex="Tính đạo hàm",
            difficulty=DifficultyLevel.MEDIUM,
            answer="f'(x) = 3x²",
            is_geometry=False,
            geometry_params=None,
            source="Test",
            misconceptions=[]
        )

        db_session.add(problem)
        await db_session.commit()
        await db_session.refresh(problem)

        assert problem.is_geometry is False
        assert problem.geometry_params is None

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_problem_difficulty_levels(self, db_session: AsyncSession):
        """Test all difficulty levels"""
        difficulties = [DifficultyLevel.EASY, DifficultyLevel.MEDIUM, DifficultyLevel.HARD]

        for difficulty in difficulties:
            problem = Problem(
                topic_id=f"test-{difficulty.value}",
                statement_latex="Test problem",
                difficulty=difficulty,
                answer="42",
                is_geometry=False,
                source="Test",
                misconceptions=[]
            )
            db_session.add(problem)

        await db_session.commit()

        # Use SQLAlchemy ORM instead of raw SQL
        result = await db_session.execute(
            select(Problem).where(Problem.difficulty == DifficultyLevel.EASY)
        )
        problems = result.scalars().all()
        assert len(problems) >= 1


class TestSessionModel:
    """Test Session model"""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_create_session(self, db_session: AsyncSession, sample_user: User, sample_problem: Problem):
        """Test creating a session"""
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

        assert session.id is not None
        assert session.user_id == sample_user.id
        assert session.problem_id == sample_problem.id
        assert session.status == SessionStatus.ACTIVE
        assert session.dialogue_state == DialogueState.REVIEW

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_session_messages(self, db_session: AsyncSession, sample_user: User):
        """Test session messages storage"""
        session = Session(
            user_id=sample_user.id,
            topic_id="test-topic",
            status=SessionStatus.ACTIVE,
            dialogue_state=DialogueState.REVIEW,
            hint_level=0,
            hint_count=0,
            fail_count=0,
            messages=[
                {"role": "user", "content": "Test message", "timestamp": datetime.now(timezone.utc).isoformat()},
                {"role": "assistant", "content": "Test response", "timestamp": datetime.now(timezone.utc).isoformat()}
            ]
        )

        db_session.add(session)
        await db_session.commit()
        await db_session.refresh(session)

        assert len(session.messages) == 2
        assert session.messages[0]["role"] == "user"
        assert session.messages[1]["role"] == "assistant"

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_session_state_transitions(self, db_session: AsyncSession, sample_user: User):
        """Test session state transitions"""
        session = Session(
            user_id=sample_user.id,
            topic_id="test-topic",
            status=SessionStatus.ACTIVE,
            dialogue_state=DialogueState.REVIEW,
            hint_level=0,
            hint_count=0,
            fail_count=0,
            messages=[]
        )

        db_session.add(session)
        await db_session.commit()

        # Transition to HEURISTIC
        session.dialogue_state = DialogueState.HEURISTIC
        session.fail_count = 1
        await db_session.commit()

        await db_session.refresh(session)
        assert session.dialogue_state == DialogueState.HEURISTIC
        assert session.fail_count == 1

        # Complete session
        session.status = SessionStatus.COMPLETED
        session.ended_at = datetime.utcnow()
        await db_session.commit()

        await db_session.refresh(session)
        assert session.status == SessionStatus.COMPLETED
        assert session.ended_at is not None


class TestProgressModel:
    """Test Progress model"""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_create_progress(self, db_session: AsyncSession, sample_user: User):
        """Test creating progress record"""
        progress = Progress(
            user_id=sample_user.id,
            topic_id="hinh-hoc.hinh-chop",
            mastery_score=0.75,
            sessions_count=5,
            last_practiced=datetime.utcnow()
        )

        db_session.add(progress)
        await db_session.commit()
        await db_session.refresh(progress)

        assert progress.user_id == sample_user.id
        assert progress.topic_id == "hinh-hoc.hinh-chop"
        assert progress.mastery_score == 0.75
        assert progress.sessions_count == 5

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_progress_composite_key(self, db_session: AsyncSession, sample_user: User):
        """Test progress composite primary key"""
        progress1 = Progress(
            user_id=sample_user.id,
            topic_id="topic-1",
            mastery_score=0.5,
            sessions_count=3
        )

        progress2 = Progress(
            user_id=sample_user.id,
            topic_id="topic-2",
            mastery_score=0.8,
            sessions_count=5
        )

        db_session.add(progress1)
        db_session.add(progress2)
        await db_session.commit()

        # Should be able to create multiple progress records for same user, different topics
        assert progress1.topic_id == "topic-1"
        assert progress2.topic_id == "topic-2"


class TestModelRelationships:
    """Test model relationships and cascading deletes"""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_cascade_delete_user_sessions(self, db_session: AsyncSession, sample_user: User):
        """Test cascading delete of user sessions"""
        # Create sessions for user
        for i in range(3):
            session = Session(
                user_id=sample_user.id,
                topic_id=f"topic-{i}",
                status=SessionStatus.ACTIVE,
                dialogue_state=DialogueState.REVIEW,
                hint_level=0,
                hint_count=0,
                fail_count=0,
                messages=[]
            )
            db_session.add(session)

        await db_session.commit()

        # Delete user
        await db_session.delete(sample_user)
        await db_session.commit()

        # Sessions should be deleted due to CASCADE
        from sqlalchemy import select
        result = await db_session.execute(
            select(Session).where(Session.user_id == sample_user.id)
        )
        sessions = result.scalars().all()
        assert len(sessions) == 0

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_cascade_delete_user_progress(self, db_session: AsyncSession, sample_user: User):
        """Test cascading delete of user progress"""
        # Create progress for user
        progress = Progress(
            user_id=sample_user.id,
            topic_id="test-topic",
            mastery_score=0.5,
            sessions_count=3
        )
        db_session.add(progress)
        await db_session.commit()

        # Delete user
        await db_session.delete(sample_user)
        await db_session.commit()

        # Progress should be deleted due to CASCADE
        from sqlalchemy import select
        result = await db_session.execute(
            select(Progress).where(Progress.user_id == sample_user.id)
        )
        progress_records = result.scalars().all()
        assert len(progress_records) == 0
