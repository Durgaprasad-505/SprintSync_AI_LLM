import enum
from sqlalchemy import Column, Integer, String, Text, Enum, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database import Base


class TaskStatus(str, enum.Enum):
    backlog = "backlog"
    in_progress = "in_progress"
    review = "review"
    done = "done"


# Valid status transitions
STATUS_TRANSITIONS: dict[TaskStatus, list[TaskStatus]] = {
    TaskStatus.backlog: [TaskStatus.in_progress],
    TaskStatus.in_progress: [TaskStatus.review, TaskStatus.backlog],
    TaskStatus.review: [TaskStatus.done, TaskStatus.in_progress],
    TaskStatus.done: [],
}


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, default="")
    status = Column(Enum(TaskStatus), default=TaskStatus.backlog, nullable=False)
    total_minutes = Column(Integer, default=0)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    owner = relationship("User", back_populates="tasks")
