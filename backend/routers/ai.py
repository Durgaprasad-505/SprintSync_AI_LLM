from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from database import get_db
from models import User, Task
from services.auth import get_current_user
from services import ai as ai_service

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/suggest")
async def suggest(
    mode: str = Query("description", enum=["description", "daily_plan"]),
    title: str = Query(None, description="Task title (required for mode=description)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    AI-powered suggestions:
    - mode=description: Draft a task description from a short title
    - mode=daily_plan: Return a concise daily plan for the signed-in user
    """
    if mode == "description":
        if not title:
            from fastapi import HTTPException
            raise HTTPException(status_code=400, detail="title is required for mode=description")
        return await ai_service.generate_task_description(title)

    # daily_plan mode
    tasks = db.query(Task).filter(Task.owner_id == current_user.id).all()
    task_list = [
        {"title": t.title, "status": t.status.value, "total_minutes": t.total_minutes}
        for t in tasks
    ]
    return await ai_service.generate_daily_plan(current_user.username, task_list)
