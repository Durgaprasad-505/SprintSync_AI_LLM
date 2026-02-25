from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from database import get_db
from models import User, Task
from services.auth import get_current_user

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("/top-users")
def top_users(
    limit: int = 5,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Top users by total minutes logged on their tasks."""
    rows = (
        db.query(User.id, User.username, func.sum(Task.total_minutes).label("total_minutes"))
        .join(Task, Task.owner_id == User.id)
        .group_by(User.id, User.username)
        .order_by(func.sum(Task.total_minutes).desc())
        .limit(limit)
        .all()
    )
    return [{"user_id": r.id, "username": r.username, "total_minutes": r.total_minutes or 0} for r in rows]


@router.get("/cycle-time")
def avg_cycle_time(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Average total_minutes per task status."""
    rows = (
        db.query(Task.status, func.avg(Task.total_minutes).label("avg_minutes"), func.count(Task.id).label("count"))
        .group_by(Task.status)
        .all()
    )
    return [
        {"status": r.status.value, "avg_minutes": round(float(r.avg_minutes or 0), 1), "count": r.count}
        for r in rows
    ]
