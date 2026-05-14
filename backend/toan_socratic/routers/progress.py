from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime, timedelta
from toan_socratic.db.database import get_db
from toan_socratic.db.models import DialogueState, Progress, Session, SessionStatus
from uuid import UUID

router = APIRouter(prefix="/api/progress", tags=["progress"])

@router.get("")
async def get_progress(user_id: str, db: AsyncSession = Depends(get_db)):
    """Get progress for a user"""
    try:
        user_uuid = UUID(user_id)
    except ValueError:
        # Return empty list for invalid user_id (new users)
        return []

    result = await db.execute(
        select(Progress).where(Progress.user_id == user_uuid)
    )
    progress_list = result.scalars().all()
    return progress_list

@router.get("/mastery")
async def get_mastery_map(user_id: str, db: AsyncSession = Depends(get_db)):
    """Get mastery map for a user"""
    try:
        user_uuid = UUID(user_id)
    except ValueError:
        # Return default mastery map for invalid user_id (new users)
        return {
            "mastery_by_topic": {},
            "sessions_this_week": 0,
            "suggested_topics": [],
            "streak_days": 0
        }

    # Get progress by topic
    result = await db.execute(
        select(Progress).where(Progress.user_id == user_uuid)
    )
    progress_list = result.scalars().all()

    mastery_by_topic = {p.topic_id: p.mastery_score for p in progress_list}
    sessions_count = sum(p.sessions_count for p in progress_list)

    # Get sessions from this week
    one_week_ago = datetime.utcnow() - timedelta(days=7)
    result = await db.execute(
        select(func.count()).select_from(Session).where(
            Session.user_id == user_uuid,
            Session.started_at >= one_week_ago,
            Session.status == SessionStatus.COMPLETED
        )
    )
    sessions_this_week = result.scalar() or 0

    # Calculate streak (simplified - consecutive days with sessions)
    result = await db.execute(
        select(Session.started_at).where(
            Session.user_id == user_uuid,
            Session.status == SessionStatus.COMPLETED
        ).order_by(Session.started_at.desc()).limit(30)
    )
    session_dates = result.scalars().all()
    streak_days = calculate_streak(session_dates)

    # Suggest topics with low mastery
    suggested_topics = [
        p.topic_id for p in progress_list
        if p.mastery_score < 0.6
    ][:3]

    return {
        "mastery_by_topic": mastery_by_topic,
        "sessions_this_week": sessions_this_week,
        "suggested_topics": suggested_topics,
        "streak_days": streak_days
    }

def calculate_streak(session_dates):
    """Calculate consecutive days with sessions"""
    if not session_dates:
        return 0

    dates = set(d.date() for d in session_dates)
    today = datetime.utcnow().date()
    streak = 0

    for i in range(30):
        check_date = today - timedelta(days=i)
        if check_date in dates:
            streak += 1
        else:
            break

    return streak
