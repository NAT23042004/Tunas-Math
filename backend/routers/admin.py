from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import get_db
from db.models import Progress, Session, SessionStatus, User
from routers.auth import require_admin

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/stats")
async def get_admin_stats(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    one_week_ago = datetime.utcnow() - timedelta(days=7)

    total_users = await db.scalar(select(func.count()).select_from(User)) or 0
    completed_sessions = await db.scalar(
        select(func.count()).select_from(Session).where(Session.status == SessionStatus.COMPLETED)
    ) or 0
    total_sessions = await db.scalar(select(func.count()).select_from(Session)) or 0
    active_students = await db.scalar(
        select(func.count(func.distinct(Session.user_id))).where(Session.started_at >= one_week_ago)
    ) or 0

    progress_rows = (
        await db.execute(select(Progress).order_by(Progress.mastery_score.asc()).limit(5))
    ).scalars().all()
    lowest_mastery_topics = [
        {"topic_id": row.topic_id, "mastery_score": row.mastery_score}
        for row in progress_rows
    ]

    geometry_sessions = await db.scalar(
        select(func.count()).select_from(Session).where(Session.topic_id.like("hinh-hoc.%"))
    ) or 0

    return {
        "total_users": total_users,
        "active_students": active_students,
        "total_sessions": total_sessions,
        "completed_sessions": completed_sessions,
        "geometry_sessions": geometry_sessions,
        "lowest_mastery_topics": lowest_mastery_topics,
    }
