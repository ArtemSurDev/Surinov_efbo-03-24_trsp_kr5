from fastapi import APIRouter, Depends, HTTPException, status, Header
from typing import Optional, List

from ..schemas import Task, TaskCreate, TaskStatusUpdate
from ..storage import TaskStorage, get_storage

router = APIRouter(prefix="/tasks", tags=["tasks"])


def get_current_user_id(x_user_id: Optional[str] = Header(None)) -> int:
    if x_user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="X-User-Id header is required"
        )

    try:
        user_id = int(x_user_id)
        return user_id
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="X-User-Id must be a valid integer"
        )


@router.post("/", response_model=Task, status_code=status.HTTP_201_CREATED)
def create_task(
        task_data: TaskCreate,
        user_id: int = Depends(get_current_user_id),
        storage: TaskStorage = Depends(get_storage)
):
    task = storage.create(task_data.model_dump(), user_id)
    return task


@router.get("/", response_model=List[Task])
def get_tasks(
        status: Optional[str] = None,
        min_priority: Optional[int] = None,
        user_id: int = Depends(get_current_user_id),
        storage: TaskStorage = Depends(get_storage)
):
    tasks = storage.get_user_tasks(user_id, status, min_priority)
    return tasks


@router.get("/{task_id}", response_model=Task)
def get_task(
        task_id: int,
        user_id: int = Depends(get_current_user_id),
        storage: TaskStorage = Depends(get_storage)
):
    task = storage.get_task(task_id)

    if task is None or task.owner_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    return task


@router.patch("/{task_id}/status", response_model=Task)
def update_task_status(
        task_id: int,
        status_update: TaskStatusUpdate,
        user_id: int = Depends(get_current_user_id),
        storage: TaskStorage = Depends(get_storage)
):
    task = storage.get_task(task_id)

    if task is None or task.owner_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    updated_task = storage.update_task_status(task_id, status_update.status.value)
    return updated_task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
        task_id: int,
        user_id: int = Depends(get_current_user_id),
        storage: TaskStorage = Depends(get_storage)
):
    task = storage.get_task(task_id)

    if task is None or task.owner_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    storage.delete_task(task_id)
    return None