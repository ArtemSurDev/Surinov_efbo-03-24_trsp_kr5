from typing import Optional
from pydantic import BaseModel, Field, field_validator
from enum import Enum


class TaskStatus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class TaskCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=80)
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.TODO
    priority: int = Field(..., ge=1, le=5)

    @field_validator("title")
    def validate_title(cls, v):
        if not v or len(v.strip()) < 3:
            raise ValueError("Title must be at least 3 characters")
        if len(v) > 80:
            raise ValueError("Title must be at most 80 characters")
        return v.strip()


class Task(TaskCreate):
    id: int
    owner_id: int


class TaskStatusUpdate(BaseModel):
    status: TaskStatus