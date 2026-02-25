from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from database import get_db
from models import User, Task, TaskStatus, STATUS_TRANSITIONS
from services.auth import get_current_user, get_admin_user

router = APIRouter(prefix="/tasks", tags=["tasks"])


class TaskOut(BaseModel):
    id: int
    title: str
    description: str
    status: TaskStatus
    total_minutes: int
    owner_id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TaskCreate(BaseModel):
    title: str
    description: str = ""
    status: TaskStatus = TaskStatus.backlog
    total_minutes: int = 0
    owner_id: Optional[int] = None  # defaults to current user


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    total_minutes: Optional[int] = None


class StatusTransition(BaseModel):
    new_status: TaskStatus


@router.get("/", response_model=list[TaskOut])
def list_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.is_admin:
        return db.query(Task).all()
    return db.query(Task).filter(Task.owner_id == current_user.id).all()


@router.post("/", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
def create_task(
    payload: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    owner_id = payload.owner_id or current_user.id
    # Non-admins can only create tasks for themselves
    if not current_user.is_admin and owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Cannot create tasks for other users")

    task = Task(
        title=payload.title,
        description=payload.description,
        status=payload.status,
        total_minutes=payload.total_minutes,
        owner_id=owner_id,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.get("/{task_id}", response_model=TaskOut)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if not current_user.is_admin and task.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed")
    return task


@router.patch("/{task_id}", response_model=TaskOut)
def update_task(
    task_id: int,
    payload: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if not current_user.is_admin and task.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed")

    if payload.title is not None:
        task.title = payload.title
    if payload.description is not None:
        task.description = payload.description
    if payload.total_minutes is not None:
        task.total_minutes = payload.total_minutes

    db.commit()
    db.refresh(task)
    return task


@router.post("/{task_id}/transition", response_model=TaskOut)
def transition_task(
    task_id: int,
    payload: StatusTransition,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if not current_user.is_admin and task.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed")

    allowed = STATUS_TRANSITIONS[task.status]
    if payload.new_status not in allowed:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot transition from '{task.status}' to '{payload.new_status}'. "
                   f"Allowed: {[s.value for s in allowed]}",
        )

    task.status = payload.new_status
    db.commit()
    db.refresh(task)
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if not current_user.is_admin and task.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed")
    db.delete(task)
    db.commit()
