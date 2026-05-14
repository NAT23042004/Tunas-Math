from sqlalchemy import Column, String, Boolean, Integer, Float, DateTime, ForeignKey, Enum as SQLEnum, Text
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime
import uuid
import enum

from db.compatibility import UUID, JSONB
from sqlalchemy import Text as Vector  # Placeholder for Vector type


Base = declarative_base()


class UserRole(str, enum.Enum):
    STUDENT = "student"
    ADMIN = "admin"


class SessionStatus(str, enum.Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class DialogueState(str, enum.Enum):
    REVIEW = "review"
    HEURISTIC = "heuristic"
    RECTIFY = "rectify"
    SUMMARIZE = "summarize"


class DifficultyLevel(str, enum.Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class User(Base):
    __tablename__ = "users"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    avatar_url = Column(String, nullable=True)
    auth_provider = Column(String, nullable=True)
    auth_subject = Column(String, nullable=True, index=True)
    role = Column(SQLEnum(UserRole), default=UserRole.STUDENT, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime, nullable=True)

    # Relationships
    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")
    progress = relationship("Progress", back_populates="user", cascade="all, delete-orphan")


class Problem(Base):
    __tablename__ = "problems"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    topic_id = Column(String, nullable=False, index=True)
    statement_latex = Column(Text, nullable=False)
    difficulty = Column(SQLEnum(DifficultyLevel), nullable=False)
    answer = Column(Text, nullable=False)
    is_geometry = Column(Boolean, default=False)
    geometry_params = Column(JSONB, nullable=True)
    source = Column(String, nullable=True)
    misconceptions = Column(JSONB, nullable=True)
    # embedding = Column(Vector, nullable=True)  # Requires pgvector extension
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    sessions = relationship("Session", back_populates="problem")


class Session(Base):
    __tablename__ = "sessions"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    problem_id = Column(UUID(as_uuid=True), ForeignKey("problems.id"), nullable=True)
    topic_id = Column(String, nullable=False)
    status = Column(SQLEnum(SessionStatus), default=SessionStatus.ACTIVE)
    dialogue_state = Column(SQLEnum(DialogueState), default=DialogueState.REVIEW)
    hint_level = Column(Integer, default=0)
    hint_count = Column(Integer, default=0)
    fail_count = Column(Integer, default=0)
    messages = Column(JSONB, nullable=False, default=list)
    summary = Column(Text, nullable=True)
    student_rating = Column(Integer, nullable=True)
    started_at = Column(DateTime, default=lambda: datetime.utcnow().replace(tzinfo=None))
    ended_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="sessions")
    problem = relationship("Problem", back_populates="sessions")


class Progress(Base):
    __tablename__ = "progress"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    topic_id = Column(String, primary_key=True)
    mastery_score = Column(Float, default=0.0)
    sessions_count = Column(Integer, default=0)
    last_practiced = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="progress")
