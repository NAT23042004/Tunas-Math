from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
from enum import Enum


class UserRole(str, Enum):
    STUDENT = "student"
    ADMIN = "admin"


class SessionStatus(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class DialogueState(str, Enum):
    REVIEW = "review"
    HEURISTIC = "heuristic"
    RECTIFY = "rectify"
    SUMMARIZE = "summarize"


class DifficultyLevel(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


# User Schemas
class UserBase(BaseModel):
    email: str
    name: str


class UserCreate(UserBase):
    pass


class UserResponse(UserBase):
    id: UUID
    role: UserRole
    created_at: datetime
    last_active: Optional[datetime] = None

    class Config:
        from_attributes = True


# Problem Schemas
class ProblemBase(BaseModel):
    topic_id: str
    statement_latex: str
    difficulty: DifficultyLevel
    answer: str
    is_geometry: bool = False
    geometry_params: Optional[Dict[str, Any]] = None
    source: Optional[str] = None
    misconceptions: Optional[List[str]] = None


class ProblemCreate(ProblemBase):
    pass


class ProblemResponse(ProblemBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


# Session Schemas
class SessionCreate(BaseModel):
    topic_id: str
    problem_id: Optional[UUID] = None
    initial_message: Optional[str] = None


class SessionMessage(BaseModel):
    role: str
    content: str
    timestamp: datetime
    tool_calls: Optional[List[Dict[str, Any]]] = None


class SessionResponse(BaseModel):
    id: UUID
    user_id: UUID
    topic_id: str
    problem_id: Optional[UUID] = None
    status: SessionStatus
    dialogue_state: DialogueState
    hint_level: int
    hint_count: int
    fail_count: int
    messages: List[SessionMessage]
    summary: Optional[str] = None
    student_rating: Optional[int] = None
    started_at: datetime
    ended_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class SessionComplete(BaseModel):
    student_rating: Optional[int] = Field(None, ge=1, le=5)


class SessionCompleteResponse(BaseModel):
    summary: str
    mastery_delta: float
    next_suggested_topic: str


# Message Schemas
class MessageCreate(BaseModel):
    content: str
    hint_requested: bool = False


class MessageResponse(BaseModel):
    role: str
    content: str
    timestamp: datetime
    tool_calls: Optional[List[Dict[str, Any]]] = None


# Progress Schemas
class ProgressResponse(BaseModel):
    user_id: UUID
    topic_id: str
    mastery_score: float
    sessions_count: int
    last_practiced: Optional[datetime] = None

    class Config:
        from_attributes = True


class MasteryMapResponse(BaseModel):
    mastery_by_topic: Dict[str, float]
    sessions_this_week: int
    suggested_topics: List[str]
    streak_days: int


# Health Schemas
class HealthResponse(BaseModel):
    status: str
    service: str
    version: str