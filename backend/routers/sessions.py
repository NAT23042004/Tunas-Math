from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from uuid import UUID
from datetime import datetime

from db.database import get_db
from db.models import Session, User, Problem, DialogueState, SessionStatus
from db.schemas import (
    SessionCreate, SessionResponse, SessionComplete,
    SessionCompleteResponse, MessageCreate, MessageResponse
)
from ai.dialogue import DialogueStateMachine, HintLevel
from ai.context_builder import SessionContextBuilder
from ai.claude_client import claude_client
from ai.prompts import format_system_prompt, GEOMETRY_TOOL


router = APIRouter(prefix="/api/sessions", tags=["sessions"])

# Initialize context builder
context_builder = SessionContextBuilder()


@router.post("", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(
    session_data: SessionCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new Socratic session"""
    # Create new session
    new_session = Session(
        topic_id=session_data.topic_id,
        problem_id=session_data.problem_id,
        status=SessionStatus.ACTIVE,
        dialogue_state=DialogueState.REVIEW,
        hint_level=0,
        hint_count=0,
        fail_count=0,
        messages=[],
        started_at=datetime.utcnow()
    )

    db.add(new_session)
    await db.commit()
    await db.refresh(new_session)

    return new_session


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get session by ID"""
    result = await db.execute(select(Session).where(Session.id == session_id))
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )

    return session


@router.post("/{session_id}/message")
async def send_message(
    session_id: UUID,
    message_data: MessageCreate,
    db: AsyncSession = Depends(get_db)
):
    """Send a message and get AI response (streaming)"""
    # Get session
    result = await db.execute(select(Session).where(Session.id == session_id))
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )

    # Add user message to session
    user_message = {
        "role": "user",
        "content": message_data.content,
        "timestamp": datetime.utcnow().isoformat()
    }
    session.messages.append(user_message)

    # Get problem context if available
    problem_context = None
    if session.problem_id:
        problem_result = await db.execute(
            select(Problem).where(Problem.id == session.problem_id)
        )
        problem = problem_result.scalar_one_or_none()
        if problem:
            problem_context = {
                "statement": problem.statement_latex,
                "difficulty": problem.difficulty.value,
                "is_geometry": problem.is_geometry,
                "geometry_params": problem.geometry_params
            }

    # Build context for AI
    context = context_builder.build_context(
        topic_id=session.topic_id,
        problem_statement=problem_context["statement"] if problem_context else "",
        dialogue_state=session.dialogue_state.value,
        fail_count=session.fail_count,
        hint_level=session.hint_level,
        conversation_history=session.messages,
        problem_context=problem_context
    )

    # Format system prompt
    system_prompt = format_system_prompt(
        dialogue_state=context["dialogue_state"],
        fail_count=context["fail_count"],
        hint_level=context["hint_level"],
        topic=context["topic"],
        problem_statement=context["problem_statement"],
        misconceptions=context["misconceptions"]
    )

    # Prepare tools if geometry problem
    tools = []
    if problem_context and problem_context.get("is_geometry"):
        tools.append(GEOMETRY_TOOL)

    # Convert messages to Claude format
    claude_messages = []
    for msg in session.messages:
        claude_messages.append({
            "role": msg["role"],
            "content": msg["content"]
        })

    # Get AI response
    try:
        if tools:
            response = await claude_client.get_response_with_tools(
                messages=claude_messages,
                system_prompt=system_prompt,
                tools=tools
            )
        else:
            response_text = await claude_client.get_response(
                messages=claude_messages,
                system_prompt=system_prompt
            )
            response = {"text": response_text, "tool_calls": []}

        # Add AI response to session
        ai_message = {
            "role": "assistant",
            "content": response["text"],
            "timestamp": datetime.utcnow().isoformat(),
            "tool_calls": response.get("tool_calls", [])
        }
        session.messages.append(ai_message)

        # Update session state
        if message_data.hint_requested:
            session.hint_count += 1
            if session.hint_level < 3:
                session.hint_level += 1

        await db.commit()
        await db.refresh(session)

        return {
            "message": ai_message,
            "session_state": {
                "dialogue_state": session.dialogue_state.value,
                "hint_level": session.hint_level,
                "fail_count": session.fail_count
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting AI response: {str(e)}"
        )


@router.put("/{session_id}/complete", response_model=SessionCompleteResponse)
async def complete_session(
    session_id: UUID,
    completion_data: SessionComplete,
    db: AsyncSession = Depends(get_db)
):
    """Mark session as complete and update progress"""
    # Get session
    result = await db.execute(select(Session).where(Session.id == session_id))
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )

    # Update session
    session.status = SessionStatus.COMPLETED
    session.ended_at = datetime.utcnow()
    session.student_rating = completion_data.student_rating

    # Generate summary (simplified for now)
    session.summary = f"Hoàn thành chủ đề {session.topic_id}"

    # Calculate mastery delta
    mastery_delta = _calculate_mastery_delta(session)

    # Update progress (simplified)
    # In real implementation, would update Progress table

    await db.commit()
    await db.refresh(session)

    return SessionCompleteResponse(
        summary=session.summary,
        mastery_delta=mastery_delta,
        next_suggested_topic=_suggest_next_topic(session.topic_id)
    )


def _calculate_mastery_delta(session: Session) -> float:
    """Calculate mastery score delta based on session performance"""
    base_gain = 0.15

    # Penalty for hints
    hint_penalty = session.hint_count * 0.20

    # Penalty for failures
    fail_penalty = session.fail_count * 0.10

    # Rating bonus
    rating_factor = (session.student_rating / 5.0) if session.student_rating else 0.7

    delta = base_gain * rating_factor * (1 - hint_penalty - fail_penalty)
    return max(0.0, min(delta, base_gain))


def _suggest_next_topic(current_topic: str) -> str:
    """Suggest next topic based on current topic"""
    # Simplified logic - in real implementation would use progress data
    topic_map = {
        "hinh-hoc.hinh-chop": "hinh-hoc.lang-tru",
        "hinh-hoc.lang-tru": "giai-tich.dao-ham",
        "giai-tich.dao-ham": "giai-tich.nguyen-ham",
        "giai-tich.nguyen-ham": "giai-tich.tich-phan",
        "giai-tich.tich-phan": "xac-suat"
    }
    return topic_map.get(current_topic, "hinh-hoc.hinh-chop")