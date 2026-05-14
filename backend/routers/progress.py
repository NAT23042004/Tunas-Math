from datetime import datetime, timedelta
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import get_db
from db.models import Progress, Session, SessionStatus, User
from routers.auth import get_current_user

router = APIRouter(prefix="/api/progress", tags=["progress"])


def calculate_streak(session_dates):
    """Calculate consecutive days with sessions."""
    if not session_dates:
        return 0

    dates = {d.date() for d in session_dates}
    today = datetime.utcnow().date()
    streak = 0

    for i in range(30):
        check_date = today - timedelta(days=i)
        if check_date in dates:
            streak += 1
        else:
            break

    return streak


async def _build_mastery_map(db: AsyncSession, user_id: UUID) -> dict:
    result = await db.execute(select(Progress).where(Progress.user_id == user_id))
    progress_list = result.scalars().all()

    mastery_by_topic = {p.topic_id: p.mastery_score for p in progress_list}

    one_week_ago = datetime.utcnow() - timedelta(days=7)
    count_result = await db.execute(
        select(func.count()).select_from(Session).where(
            Session.user_id == user_id,
            Session.started_at >= one_week_ago,
            Session.status == SessionStatus.COMPLETED,
        )
    )
    sessions_this_week = count_result.scalar() or 0

    dates_result = await db.execute(
        select(Session.started_at).where(
            Session.user_id == user_id,
            Session.status == SessionStatus.COMPLETED,
        ).order_by(Session.started_at.desc()).limit(30)
    )
    session_dates = dates_result.scalars().all()

    weekly_activity = []
    today = datetime.utcnow().date()
    for offset in range(6, -1, -1):
        day = today - timedelta(days=offset)
        weekly_activity.append(
            {
                "date": day.isoformat(),
                "sessions": sum(1 for session_date in session_dates if session_date.date() == day),
            }
        )

    suggested_topics = [p.topic_id for p in progress_list if p.mastery_score < 0.6][:3]

    return {
        "mastery_by_topic": mastery_by_topic,
        "sessions_this_week": sessions_this_week,
        "suggested_topics": suggested_topics,
        "streak_days": calculate_streak(session_dates),
        "weekly_activity": weekly_activity,
    }


@router.get("")
async def get_progress(user_id: str, db: AsyncSession = Depends(get_db)):
    """Legacy progress endpoint retained for compatibility."""
    try:
        user_uuid = UUID(user_id)
    except ValueError:
        return []

    result = await db.execute(select(Progress).where(Progress.user_id == user_uuid))
    return result.scalars().all()


@router.get("/mastery")
async def get_mastery_map(user_id: str, db: AsyncSession = Depends(get_db)):
    """Legacy mastery endpoint retained for compatibility."""
    try:
        user_uuid = UUID(user_id)
    except ValueError:
        return {
            "mastery_by_topic": {},
            "sessions_this_week": 0,
            "suggested_topics": [],
            "streak_days": 0,
            "weekly_activity": [],
        }

    return await _build_mastery_map(db, user_uuid)


@router.get("/me")
async def get_my_progress(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await _build_mastery_map(db, current_user.id)
